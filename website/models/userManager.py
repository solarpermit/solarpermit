from django.db import models
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)

# Extend the UserManager in order to allow end-to-end functional
# testing of user-creation and login. We want to be able to run the
# functional test suite all the time, even against the production
# database. This means that tests involving anything that writes to
# the database are tricky; we don't want a test that creates a new
# user account to fail merely because it was run twice, for instance.
class TestableUserManager(BaseUserManager):
    def _create_user(self, username, email, password,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates a User with the given username, email and password.
        """
        now = timezone.now()
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        return user

    def create_user(self, username, email, password=None, **extra_fields):
        mailbox, domain = email.split('@'); # a very bogus way to parse an email address, but good enough for our purposes
        if domain != 'testing.solarpermit.org':
            return super(TestableUserManager, self).create_user(username, email, password);
        if mailbox == "new":
            # creates a new user, but does not save it so that it never fails due to a duplicate address
            return self._create_user(username, email, password, False, False, **extra_fields);
