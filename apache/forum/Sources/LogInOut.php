<?php

/**
 * Simple Machines Forum (SMF)
 *
 * @package SMF
 * @author Simple Machines http://www.simplemachines.org
 * @copyright 2011 Simple Machines
 * @license http://www.simplemachines.org/about/smf/license.php BSD
 *
 * @version 2.0.4
 */

if (!defined('SMF'))
	die('Hacking attempt...');

/*	This file is concerned pretty entirely, as you see from its name, with
	logging in and out members, and the validation of that.  It contains:

	void Login()
		- shows a page for the user to type in their username and password.
		- caches the referring URL in $_SESSION['login_url'].
		- uses the Login template and language file with the login sub
		  template.
		- if you are using a wireless device, uses the protocol_login sub
		  template in the Wireless template.
		- accessed from ?action=login.

	void Login2()
		- actually logs you in and checks that login was successful.
		- employs protection against a specific IP or user trying to brute
		  force a login to an account.
		- on error, uses the same templates Login() uses.
		- upgrades password encryption on login, if necessary.
		- after successful login, redirects you to $_SESSION['login_url'].
		- accessed from ?action=login2, by forms.

	void Logout(bool internal = false)
		- logs the current user out of their account.
		- requires that the session hash is sent as well, to prevent automatic
		  logouts by images or javascript.
		- doesn't check the session if internal is true.
		- redirects back to $_SESSION['logout_url'], if it exists.
		- accessed via ?action=logout;session_var=...

	string md5_hmac(string data, string key)
		- old style SMF 1.0.x/YaBB SE 1.5.x hashing.
		- returns the HMAC MD5 of data with key.

	string phpBB3_password_check(string passwd, string passwd_hash)
		- custom encryption for phpBB3 based passwords.

	void validatePasswordFlood(id_member, password_flood_value = false, was_correct = false)
		- this function helps protect against brute force attacks on a member's password.
*/

// Ask them for their login information.
function Login()
{
	global $txt, $context, $scripturl;

	// In wireless?  If so, use the correct sub template.
	if (WIRELESS)
		$context['sub_template'] = WIRELESS_PROTOCOL . '_login';
	// Otherwise, we need to load the Login template/language file.
	else
	{
		loadLanguage('Login');
		loadTemplate('Login');
		$context['sub_template'] = 'login';
	}

	// Get the template ready.... not really much else to do.
	$context['page_title'] = $txt['login'];
	$context['default_username'] = &$_REQUEST['u'];
	$context['default_password'] = '';
	$context['never_expire'] = false;

	// Add the login chain to the link tree.
	$context['linktree'][] = array(
		'url' => $scripturl . '?action=login',
		'name' => $txt['login'],
	);

	// Set the login URL - will be used when the login process is done (but careful not to send us to an attachment).
	if (isset($_SESSION['old_url']) && strpos($_SESSION['old_url'], 'dlattach') === false && preg_match('~(board|topic)[=,]~', $_SESSION['old_url']) != 0)
		$_SESSION['login_url'] = $_SESSION['old_url'];
	else
		unset($_SESSION['login_url']);
}






//LSS: Plugin used for PBKDF2 password hashing
/*
 * Password hashing with PBKDF2.
 * Author: havoc AT defuse.ca
 * www: https://defuse.ca/php-pbkdf2.htm
 */

// These constants may be changed without breaking existing hashes.
define("PBKDF2_HASH_ALGORITHM", "sha256");
define("PBKDF2_ITERATIONS", 1000);
define("PBKDF2_SALT_BYTES", 24);
define("PBKDF2_HASH_BYTES", 24);

define("HASH_SECTIONS", 4);
define("HASH_ALGORITHM_INDEX", 0);
define("HASH_ITERATION_INDEX", 1);
define("HASH_SALT_INDEX", 2);
define("HASH_PBKDF2_INDEX", 3);

function create_hash($password)
{
    // format: algorithm:iterations:salt:hash
    $salt = base64_encode(mcrypt_create_iv(PBKDF2_SALT_BYTES, MCRYPT_DEV_URANDOM));
    return PBKDF2_HASH_ALGORITHM . ":" . PBKDF2_ITERATIONS . ":" .  $salt . ":" . 
        base64_encode(pbkdf2(
            PBKDF2_HASH_ALGORITHM,
            $password,
            $salt,
            PBKDF2_ITERATIONS,
            PBKDF2_HASH_BYTES,
            true
        ));
}

function validate_password($password, $good_hash)
{
    $params = explode(":", $good_hash);
    if(count($params) < HASH_SECTIONS)
       return false; 
    $pbkdf2 = base64_decode($params[HASH_PBKDF2_INDEX]);
    return slow_equals(
        $pbkdf2,
        pbkdf2(
            $params[HASH_ALGORITHM_INDEX],
            $password,
            $params[HASH_SALT_INDEX],
            (int)$params[HASH_ITERATION_INDEX],
            strlen($pbkdf2),
            true
        )
    );
}

// Compares two strings $a and $b in length-constant time.
function slow_equals($a, $b)
{
    $diff = strlen($a) ^ strlen($b);
    for($i = 0; $i < strlen($a) && $i < strlen($b); $i++)
    {
        $diff |= ord($a[$i]) ^ ord($b[$i]);
    }
    return $diff === 0; 
}

/*
 * PBKDF2 key derivation function as defined by RSA's PKCS #5: https://www.ietf.org/rfc/rfc2898.txt
 * $algorithm - The hash algorithm to use. Recommended: SHA256
 * $password - The password.
 * $salt - A salt that is unique to the password.
 * $count - Iteration count. Higher is better, but slower. Recommended: At least 1000.
 * $key_length - The length of the derived key in bytes.
 * $raw_output - If true, the key is returned in raw binary format. Hex encoded otherwise.
 * Returns: A $key_length-byte key derived from the password and salt.
 *
 * Test vectors can be found here: https://www.ietf.org/rfc/rfc6070.txt
 *
 * This implementation of PBKDF2 was originally created by https://defuse.ca
 * With improvements by http://www.variations-of-shadow.com
 */
function pbkdf2($algorithm, $password, $salt, $count, $key_length, $raw_output = false)
{
    $algorithm = strtolower($algorithm);
    if(!in_array($algorithm, hash_algos(), true))
        //die('PBKDF2 ERROR: Invalid hash algorithm.');
		return;
    if($count <= 0 || $key_length <= 0)
        //die('PBKDF2 ERROR: Invalid parameters.');
		return;
		
    $hash_length = strlen(hash($algorithm, "", true));
    $block_count = ceil($key_length / $hash_length);

    $output = "";
    for($i = 1; $i <= $block_count; $i++) {
        // $i encoded as 4 bytes, big endian.
        $last = $salt . pack("N", $i);
        // first iteration
        $last = $xorsum = hash_hmac($algorithm, $last, $password, true);
        // perform the other $count - 1 iterations
        for ($j = 1; $j < $count; $j++) {
            $xorsum ^= ($last = hash_hmac($algorithm, $last, $password, true));
        }
        $output .= $xorsum;
    }

    if($raw_output)
        return substr($output, 0, $key_length);
    else
        return bin2hex(substr($output, 0, $key_length));
}

function Login2()
{
	global $txt, $scripturl, $user_info, $user_settings, $smcFunc;
	global $cookiename, $maintenance, $modSettings, $context, $sc, $sourcedir;
	


// Load cookie authentication stuff.
	require_once($sourcedir . '/Subs-Auth.php');

	if (isset($_GET['sa']) && $_GET['sa'] == 'salt' && !$user_info['is_guest'])
	{
		if (isset($_COOKIE[$cookiename]) && preg_match('~^a:[34]:\{i:0;(i:\d{1,6}|s:[1-8]:"\d{1,8}");i:1;s:(0|40):"([a-fA-F0-9]{40})?";i:2;[id]:\d{1,14};(i:3;i:\d;)?\}$~', $_COOKIE[$cookiename]) === 1)
			list (, , $timeout) = @unserialize($_COOKIE[$cookiename]);
		elseif (isset($_SESSION['login_' . $cookiename]))
			list (, , $timeout) = @unserialize($_SESSION['login_' . $cookiename]);
		else
			trigger_error('Login2(): Cannot be logged in without a session or cookie', E_USER_ERROR);

		$user_settings['password_salt'] = substr(md5(mt_rand()), 0, 4);
		updateMemberData($user_info['id'], array('password_salt' => $user_settings['password_salt']));

		setLoginCookie($timeout - time(), $user_info['id'], sha1($user_settings['passwd'] . $user_settings['password_salt']));

		redirectexit('action=login2;sa=check;member=' . $user_info['id'], $context['server']['needs_login_fix']);
	}
	// Double check the cookie...
	elseif (isset($_GET['sa']) && $_GET['sa'] == 'check')
	{
		// Strike!  You're outta there!
		if ($_GET['member'] != $user_info['id'])
			fatal_lang_error('login_cookie_error', false);

		// Some whitelisting for login_url...
		if (empty($_SESSION['login_url']))
			redirectexit();
		else
		{
			// Best not to clutter the session data too much...
			$temp = $_SESSION['login_url'];
			unset($_SESSION['login_url']);

			redirectexit($temp);
		}
	}

	// Beyond this point you are assumed to be a guest trying to login.
	if (!$user_info['is_guest'])
		redirectexit();

	// Are you guessing with a script?
	spamProtection('login');

	// Set the login_url if it's not already set (but careful not to send us to an attachment).
	if (empty($_SESSION['login_url']) && isset($_SESSION['old_url']) && strpos($_SESSION['old_url'], 'dlattach') === false && preg_match('~(board|topic)[=,]~', $_SESSION['old_url']) != 0)
		$_SESSION['login_url'] = $_SESSION['old_url'];

	// Been guessing a lot, haven't we?
	if (isset($_SESSION['failed_login']) && $_SESSION['failed_login'] >= $modSettings['failed_login_threshold'] * 3)
		fatal_lang_error('login_threshold_fail', 'critical');

	// Set up the cookie length.  (if it's invalid, just fall through and use the default.)
	if (isset($_POST['cookieneverexp']) || (!empty($_POST['cookielength']) && $_POST['cookielength'] == -1))
		$modSettings['cookieTime'] = 3153600;
	elseif (!empty($_POST['cookielength']) && ($_POST['cookielength'] >= 1 || $_POST['cookielength'] <= 525600))
		$modSettings['cookieTime'] = (int) $_POST['cookielength'];

	loadLanguage('Login');
	// Load the template stuff - wireless or normal.
	if (WIRELESS)
		$context['sub_template'] = WIRELESS_PROTOCOL . '_login';
	else
	{
		loadTemplate('Login');
		$context['sub_template'] = 'login';
	}

	// Set up the default/fallback stuff.
	$context['default_username'] = isset($_POST['user']) ? preg_replace('~&amp;#(\\d{1,7}|x[0-9a-fA-F]{1,6});~', '&#\\1;', htmlspecialchars($_POST['user'])) : '';
	$context['default_password'] = '';
	$context['never_expire'] = $modSettings['cookieTime'] == 525600 || $modSettings['cookieTime'] == 3153600;
	$context['login_errors'] = array($txt['error_occured']);
	$context['page_title'] = $txt['login'];

	// Add the login chain to the link tree.
	$context['linktree'][] = array(
		'url' => $scripturl . '?action=login',
		'name' => $txt['login'],
	);

	if (!empty($_POST['openid_identifier']) && !empty($modSettings['enableOpenID']))
	{
		require_once($sourcedir . '/Subs-OpenID.php');
		if (($open_id = smf_openID_validate($_POST['openid_identifier'])) !== 'no_data')
			return $open_id;
	}

	// You forgot to type your username, dummy!
	if (!isset($_POST['user']) || $_POST['user'] == '')
	{
		$context['login_errors'] = array($txt['need_username']);
		return;
	}

	// Hmm... maybe 'admin' will login with no password. Uhh... NO!
	if ((!isset($_POST['passwrd']) || $_POST['passwrd'] == '') && (!isset($_POST['hash_passwrd']) || strlen($_POST['hash_passwrd']) != 40))
	{
		$context['login_errors'] = array($txt['no_password']);
		return;
	}

	// No funky symbols either.
	if (preg_match('~[<>&"\'=\\\]~', preg_replace('~(&#(\\d{1,7}|x[0-9a-fA-F]{1,6});)~', '', $_POST['user'])) != 0)
	{
		$context['login_errors'] = array($txt['error_invalid_characters_username']);
		return;
	}

	// Are we using any sort of integration to validate the login?
	if (in_array('retry', call_integration_hook('integrate_validate_login', array($_POST['user'], isset($_POST['hash_passwrd']) && strlen($_POST['hash_passwrd']) == 40 ? $_POST['hash_passwrd'] : null, $modSettings['cookieTime'])), true))
	{
		$context['login_errors'] = array($txt['login_hash_error']);
		$context['disable_login_hashing'] = true;
		return;
	}

	//LSS: BEGIN Solar Permit Login Integration
	$request = '';
		$username = $_POST['user'];
		$password = $_POST['passwrd'];
		
		global $solar_db_name, $solar_db_host, $solar_db_username, $solar_db_password, $solar_db_port;
		
		$solar_mysql = new mysqli($solar_db_host . ':' . $solar_db_port, $solar_db_username, $solar_db_password, $solar_db_name);
		$username = $solar_mysql->real_escape_string($username);
	
		
		//query against solarpermit db for logins
		//hotfix 8-29-13
		$query = $solar_mysql->query("SELECT * FROM `auth_user` WHERE (`username` = '$username' OR `email` = '$username') AND `is_active` = '1' LIMIT 1");
		if ($query === false || $query->num_rows == 0)
		{
			$context['login_errors'] = array($txt['username_no_exist']);
				return;
			//bad username/password
		}
		$row = $query->fetch_array();
		$solar_mysql->close();
		$hashed_pass = $row['password'];
		$hashed_pass = explode('$', $hashed_pass);
		
		
		$password = pbkdf2("SHA256", $password, $hashed_pass[2], $hashed_pass[1], strlen(base64_decode($hashed_pass[3])), true);
		if ($password == base64_decode($hashed_pass[3]))
		{
			//login successful
			global $db_name, $db_server, $db_user, $db_passwd;
			
			//LSS: further SolarPermit Login Integration
			
			$mysqli = new mysqli($db_server, $db_user, $db_passwd, $db_name);
			$solar_mysql = new mysqli($solar_db_host . ':' . $solar_db_port, $solar_db_username, $solar_db_password, $solar_db_name);
		
			$username = $mysqli->real_escape_string($_POST['user']);
			$row = null;
			//leftover debugs, feel free to ignore these
			//die("SELECT * FROM `smf_members` WHERE `member_name` = '$username' LIMIT 1;");
			//$query = $mysqli->query("SELECT * FROM `smf_members` WHERE `member_name` = '$username' LIMIT 1;");
			//hotfix 8-29-13
			$query = $solar_mysql->query("SELECT * FROM `auth_user` WHERE `username` = '$username' OR `email`='$username' LIMIT 1");
			$row = $query->fetch_array();
			
			$grp = 0;
			//makes them an admin if they are admins in solarpermit
			if ($row['is_staff'] == 1 || $row['is_superuser'] == 1)
				$grp = 1;
			
			//replicate user to SMF's DB, update relevant info on each login
			
			$orgs = "";
			//get organization info
			$query = $solar_mysql->query("SELECT `organization_id`,`user_id` FROM `website_organizationmember` WHERE `user_id` = '" . $row['id'] . "';");
			while ($orgrow = $query->fetch_array()) 
			{
				$query2 = $solar_mysql->query("SELECT `name` FROM `website_organization` WHERE `id` = '" . $orgrow['organization_id'] . "';");
				while ($orgname = $query2->fetch_array())
				{
					$orgs .= $orgname['name'] . ', ';
				}
			}
			$orgs = trim($orgs, ', ');
			$orgs = $solar_mysql->real_escape_string($orgs);

			$username = $row['username'];
			$_POST['user'] = $username;
			$displayname = $row['username'];
			
			//check display preferences

			$isrealname = $solar_mysql->query("SELECT `display_preference` FROM `website_userdetail` WHERE `user_id` = '" . $row['id'] . "';");
			if ($isrealname->num_rows > 0)
			{
				$isrealname = $isrealname->fetch_array();
				$isrealname = $isrealname['display_preference'];
				if ($isrealname == 'realname')
					$displayname = $row['first_name'] . ' ' . $row['last_name'];
			}
			
			$displayname = $mysqli->real_escape_string($displayname);
			
			$mysqli->query("INSERT INTO `smf_members`(`id_member`,`id_group`,`real_name`,`passwd`,`is_activated`,`member_name`,`buddy_list`,`message_labels`,`openid_uri`,`signature`,`ignore_boards`) 
													  VALUES('" . $row['id'] . "','" . $grp  . "','" . $displayname . "','DJANGO AUTH','1','" . $username . "','','','','','') 
													  ON DUPLICATE KEY UPDATE `id_group`='$grp', `real_name` = '" . $displayname . "', `member_name`='" . $username . "';");

			//check if custom fields have been added or not
			$count = $mysqli->query("SELECT * FROM `smf_custom_fields` WHERE `id_field` = 200 OR `id_field` = 201;");
			$count = $count->num_rows;
			if ($count != 2)
			{
				//one or both missing, create them
				$mysqli->query("INSERT INTO `smf_custom_fields` (`id_field`, `col_name`, `field_name`, `field_desc`, `field_type`, `field_length`, `field_options`, `mask`, `show_reg`, `show_display`, `show_profile`, `private`, `active`, `bbc`, `can_search`, `default_value`, `enclose`, `placement`) VALUES
(200, 'cust_solarp', 'Organization', 'Solar Permit Organization', 'text', 255, '', 'nohtml', 0, 1, 'forumprofile', 1, 1, 0, 1, '', '', 0),
(201, 'cust_displa', 'Display Organization', 'Choose whether or not to display your organization on your posts.', 'radio', 255, 'Yes,No', 'nohtml', 0, 1, 'forumprofile', 1, 1, 0, 0, 'Yes', '', 0);");
			}
			
			//apply organization data to user
			$mysqli->query("INSERT INTO `smf_themes`(`id_member`,`id_theme`,`variable`,`value`)
								VALUES('" . $row['id'] . "', '1', 'cust_solarp', '" . $orgs . "')
								ON DUPLICATE KEY UPDATE
								`value`='$orgs';");
	
		$solar_mysql->close();
		$mysqli->close();
		
	}
	else
	{
		$context['login_errors'] = array($txt['username_no_exist']);
			return;
		//bad username/password
	}
	
	
	//LSS: END Solar permit Login Integration
	$request = $smcFunc['db_query']('', '
		SELECT passwd, id_member, id_group, lngfile, is_activated, email_address, additional_groups, member_name, password_salt,
			openid_uri, passwd_flood
		FROM {db_prefix}members
		WHERE ' . ($smcFunc['db_case_sensitive'] ? 'LOWER(member_name) = LOWER({string:user_name})' : 'member_name = {string:user_name}') . '
		LIMIT 1',
		array(
			'user_name' => $smcFunc['db_case_sensitive'] ? strtolower($_POST['user']) : $_POST['user'],
		)
	);
	$user_settings = $smcFunc['db_fetch_assoc']($request);
	$smcFunc['db_free_result']($request);

	DoLogin();

}


function checkActivation()
{
	global $context, $txt, $scripturl, $user_settings, $modSettings;

	if (!isset($context['login_errors']))
		$context['login_errors'] = array();

	// What is the true activation status of this account?
	$activation_status = $user_settings['is_activated'] > 10 ? $user_settings['is_activated'] - 10 : $user_settings['is_activated'];

	// Check if the account is activated - COPPA first...
	if ($activation_status == 5)
	{
		$context['login_errors'][] = $txt['coppa_no_concent'] . ' <a href="' . $scripturl . '?action=coppa;member=' . $user_settings['id_member'] . '">' . $txt['coppa_need_more_details'] . '</a>';
		return false;
	}
	// Awaiting approval still?
	elseif ($activation_status == 3)
		fatal_lang_error('still_awaiting_approval', 'user');
	// Awaiting deletion, changed their mind?
	elseif ($activation_status == 4)
	{
		if (isset($_REQUEST['undelete']))
		{
			updateMemberData($user_settings['id_member'], array('is_activated' => 1));
			updateSettings(array('unapprovedMembers' => ($modSettings['unapprovedMembers'] > 0 ? $modSettings['unapprovedMembers'] - 1 : 0)));
		}
		else
		{
			$context['disable_login_hashing'] = true;
			$context['login_errors'][] = $txt['awaiting_delete_account'];
			$context['login_show_undelete'] = true;
			return false;
		}
	}
	// Standard activation?
	elseif ($activation_status != 1)
	{
		log_error($txt['activate_not_completed1'] . ' - <span class="remove">' . $user_settings['member_name'] . '</span>', false);

		$context['login_errors'][] = $txt['activate_not_completed1'] . ' <a href="' . $scripturl . '?action=activate;sa=resend;u=' . $user_settings['id_member'] . '">' . $txt['activate_not_completed2'] . '</a>';
		return false;
	}
	return true;
}

function DoLogin()
{
	global $txt, $scripturl, $user_info, $user_settings, $smcFunc;
	global $cookiename, $maintenance, $modSettings, $context, $sourcedir;

	// Load cookie authentication stuff.
	require_once($sourcedir . '/Subs-Auth.php');

	// Call login integration functions.
	call_integration_hook('integrate_login', array($user_settings['member_name'], isset($_POST['hash_passwrd']) && strlen($_POST['hash_passwrd']) == 40 ? $_POST['hash_passwrd'] : null, $modSettings['cookieTime']));

	// Get ready to set the cookie...
	$username = $user_settings['member_name'];
	$user_info['id'] = $user_settings['id_member'];

	// Bam!  Cookie set.  A session too, just in case.
	setLoginCookie(60 * $modSettings['cookieTime'], $user_settings['id_member'], sha1($user_settings['passwd'] . $user_settings['password_salt']));

	// Reset the login threshold.
	if (isset($_SESSION['failed_login']))
		unset($_SESSION['failed_login']);

	$user_info['is_guest'] = false;
	$user_settings['additional_groups'] = explode(',', $user_settings['additional_groups']);
	$user_info['is_admin'] = $user_settings['id_group'] == 1 || in_array(1, $user_settings['additional_groups']);

	// Are you banned?
	is_not_banned(true);

	// An administrator, set up the login so they don't have to type it again.
	if ($user_info['is_admin'] && isset($user_settings['openid_uri']) && empty($user_settings['openid_uri']))
	{
		$_SESSION['admin_time'] = time();
		unset($_SESSION['just_registered']);
	}

	// Don't stick the language or theme after this point.
	unset($_SESSION['language'], $_SESSION['id_theme']);

	// First login?
	$request = $smcFunc['db_query']('', '
		SELECT last_login
		FROM {db_prefix}members
		WHERE id_member = {int:id_member}
			AND last_login = 0',
		array(
			'id_member' => $user_info['id'],
		)
	);
	if ($smcFunc['db_num_rows']($request) == 1)
		$_SESSION['first_login'] = true;
	else
		unset($_SESSION['first_login']);
	$smcFunc['db_free_result']($request);

	// You've logged in, haven't you?
	updateMemberData($user_info['id'], array('last_login' => time(), 'member_ip' => $user_info['ip'], 'member_ip2' => $_SERVER['BAN_CHECK_IP']));

	// Get rid of the online entry for that old guest....
	$smcFunc['db_query']('', '
		DELETE FROM {db_prefix}log_online
		WHERE session = {string:session}',
		array(
			'session' => 'ip' . $user_info['ip'],
		)
	);
	$_SESSION['log_time'] = 0;

	// Just log you back out if it's in maintenance mode and you AREN'T an admin.
	if (empty($maintenance) || allowedTo('admin_forum'))
		redirectexit('action=login2;sa=check;member=' . $user_info['id'], $context['server']['needs_login_fix']);
	else
		redirectexit('action=logout;' . $context['session_var'] . '=' . $context['session_id'], $context['server']['needs_login_fix']);
}

// Log the user out.
function Logout($internal = false, $redirect = true)
{
	global $sourcedir, $user_info, $user_settings, $context, $modSettings, $smcFunc;

	// Make sure they aren't being auto-logged out.
	if (!$internal)
		//checkSession('get');

	require_once($sourcedir . '/Subs-Auth.php');

	if (isset($_SESSION['pack_ftp']))
		$_SESSION['pack_ftp'] = null;

	// They cannot be open ID verified any longer.
	if (isset($_SESSION['openid']))
		unset($_SESSION['openid']);

	// It won't be first login anymore.
	unset($_SESSION['first_login']);

	// Just ensure they aren't a guest!
	if (!$user_info['is_guest'])
	{
		// Pass the logout information to integrations.
		call_integration_hook('integrate_logout', array($user_settings['member_name']));

		// If you log out, you aren't online anymore :P.
		$smcFunc['db_query']('', '
			DELETE FROM {db_prefix}log_online
			WHERE id_member = {int:current_member}',
			array(
				'current_member' => $user_info['id'],
			)
		);
	}

	$_SESSION['log_time'] = 0;

	// Empty the cookie! (set it in the past, and for id_member = 0)
	setLoginCookie(-3600, 0);

	// Off to the merry board index we go!
	if ($redirect)
	{
		if (empty($_SESSION['logout_url']))
			redirectexit('', $context['server']['needs_login_fix']);
		else
		{
			$temp = $_SESSION['logout_url'];
			unset($_SESSION['logout_url']);

			redirectexit($temp, $context['server']['needs_login_fix']);
		}
	}
}

// MD5 Encryption used for older passwords.
function md5_hmac($data, $key)
{
	$key = str_pad(strlen($key) <= 64 ? $key : pack('H*', md5($key)), 64, chr(0x00));
	return md5(($key ^ str_repeat(chr(0x5c), 64)) . pack('H*', md5(($key ^ str_repeat(chr(0x36), 64)) . $data)));
}

// Special encryption used by phpBB3.
function phpBB3_password_check($passwd, $passwd_hash)
{
	// Too long or too short?
	if (strlen($passwd_hash) != 34)
		return;

	// Range of characters allowed.
	$range = './0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';

	// Tests
	$strpos = strpos($range, $passwd_hash[3]);
	$count = 1 << $strpos;
	$count2 = $count;
	$salt = substr($passwd_hash, 4, 8);

	// Things are done differently for PHP 5.
	if (@version_compare(PHP_VERSION, '5') >= 0)
	{
		$hash = md5($salt . $passwd, true);
		for (; $count != 0; --$count)
			$hash = md5($hash . $passwd, true);
	}
	else
	{
		$hash = pack('H*', md5($salt . $passwd));
		for (; $count != 0; --$count)
			$hash = pack('H*', md5($hash . $passwd));
	}

	$output = substr($passwd_hash, 0, 12);
	$i = 0;
	while ($i < 16)
	{
		$value = ord($hash[$i++]);
		$output .= $range[$value & 0x3f];

		if ($i < 16)
			$value |= ord($hash[$i]) << 8;

		$output .= $range[($value >> 6) & 0x3f];

		if ($i++ >= 16)
			break;

		if ($i < 16)
			$value |= ord($hash[$i]) << 16;

		$output .= $range[($value >> 12) & 0x3f];

		if ($i++ >= 16)
			break;

		$output .= $range[($value >> 18) & 0x3f];
	}

	// Return now.
	return $output;
}

// This protects against brute force attacks on a member's password. Importantly even if the password was right we DON'T TELL THEM!
function validatePasswordFlood($id_member, $password_flood_value = false, $was_correct = false)
{
	global $smcFunc, $cookiename, $sourcedir;

	// As this is only brute protection, we allow 5 attempts every 10 seconds.

	// Destroy any session or cookie data about this member, as they validated wrong.
	require_once($sourcedir . '/Subs-Auth.php');
	setLoginCookie(-3600, 0);

	if (isset($_SESSION['login_' . $cookiename]))
		unset($_SESSION['login_' . $cookiename]);

	// We need a member!
	if (!$id_member)
	{
		// Redirect back!
		redirectexit();

		// Probably not needed, but still make sure...
		fatal_lang_error('no_access', false);
	}

	// Right, have we got a flood value?
	if ($password_flood_value !== false)
		@list ($time_stamp, $number_tries) = explode('|', $password_flood_value);

	// Timestamp or number of tries invalid?
	if (empty($number_tries) || empty($time_stamp))
	{
		$number_tries = 0;
		$time_stamp = time();
	}

	// They've failed logging in already
	if (!empty($number_tries))
	{
		// Give them less chances if they failed before
		$number_tries = $time_stamp < time() - 20 ? 2 : $number_tries;

		// They are trying too fast, make them wait longer
		if ($time_stamp < time() - 10)
			$time_stamp = time();
	}

	$number_tries++;

	// Broken the law?
	if ($number_tries > 5)
		fatal_lang_error('login_threshold_brute_fail', 'critical');

	// Otherwise set the members data. If they correct on their first attempt then we actually clear it, otherwise we set it!
	updateMemberData($id_member, array('passwd_flood' => $was_correct && $number_tries == 1 ? '' : $time_stamp . '|' . $number_tries));

}

?>