SELECT * FROM   (
            SELECT
                   website_answerreference.id,
                   website_answerreference.question_id,
                    website_question.display_order,
                    website_questioncategory.display_order AS cat_display_order
            FROM
                    website_answerreference,
                    website_question,
                    website_questioncategory,
                    auth_user,
                    website_userdetail
            WHERE
                    website_answerreference.jurisdiction_id = 2
                    AND website_question.id = website_answerreference.question_id
                    AND website_questioncategory.id = website_question.category_id
                    AND auth_user.id = website_answerreference.creator_id
                    AND website_userdetail.user_id = website_answerreference.creator_id
                    AND website_question.accepted = '1'
                    AND (
                            (
                                    (
                                            website_answerreference.approval_status = 'A'
                                            AND website_question.has_multivalues = '0'
                                            AND website_answerreference.create_datetime = (
                                                    SELECT
                                                            MAX(create_datetime)
                                                    FROM
                                                            website_answerreference AS temp_table
                                                    WHERE
                                                            temp_table.question_id = website_answerreference.question_id
                                                            AND temp_table.jurisdiction_id = website_answerreference.jurisdiction_id
                                                            AND temp_table.approval_status = 'A'
                                            )
                                    ) OR (
                                            website_answerreference.approval_status = 'P'
                                            AND website_question.has_multivalues = '0'
                                            AND website_answerreference.create_datetime != (
                                                    SELECT
                                                            MAX(create_datetime)
                                                    FROM
                                                            website_answerreference AS temp_table
                                                    WHERE
                                                            temp_table.question_id = website_answerreference.question_id
                                                            AND temp_table.jurisdiction_id = website_answerreference.jurisdiction_id
                                                            AND temp_table.approval_status = 'A'
                                            )
                                    )
                            ) OR (
                                    (
                                            website_question.has_multivalues = '1'
                                            AND (
                                                    website_answerreference.approval_status = 'A'
                                                    OR website_answerreference.approval_status = 'P'
                                            )
                                    )
                            ) OR (
                                    website_answerreference.approval_status = 'P'
                                    AND (
                                            SELECT
                                                    MAX(create_datetime)
                                            FROM
                                                    website_answerreference AS temp_table
                                            WHERE
                                                    temp_table.question_id = website_answerreference.question_id
                                                    AND temp_table.jurisdiction_id = website_answerreference.jurisdiction_id
                                                    AND temp_table.approval_status = 'A'
                                    ) IS NULL
                            )
                    )
            ) AS sorting_table
    UNION SELECT
                   NULL AS id,
                   website_question.id AS question_id,
                    website_question.display_order,
                    website_questioncategory.display_order AS cat_display_order
    FROM
            website_question,
                    website_answerreference,
            website_questioncategory
    WHERE
            website_questioncategory.id = website_question.category_id
            AND website_questioncategory.accepted = '1' 
            AND website_question.accepted = '1'
                    AND (
                            (
                                    (
                                            website_answerreference.approval_status = 'A'
                                            AND website_question.has_multivalues = '0'
                                            AND website_answerreference.create_datetime = (
                                                    SELECT
                                                            MAX(create_datetime)
                                                    FROM
                                                            website_answerreference AS temp_table
                                                    WHERE
                                                            temp_table.question_id = website_answerreference.question_id
                                                            AND temp_table.jurisdiction_id = website_answerreference.jurisdiction_id
                                                            AND temp_table.approval_status = 'A'
                                            )
                                    ) OR (
                                            website_answerreference.approval_status = 'P'
                                            AND website_question.has_multivalues = '0'
                                            AND website_answerreference.create_datetime != (
                                                    SELECT
                                                            MAX(create_datetime)
                                                    FROM
                                                            website_answerreference AS temp_table
                                                    WHERE
                                                            temp_table.question_id = website_answerreference.question_id
                                                            AND temp_table.jurisdiction_id = website_answerreference.jurisdiction_id
                                                            AND temp_table.approval_status = 'A'
                                            )
                                    )
                            ) OR (
                                    (
                                            website_question.has_multivalues = '1'
                                            AND (
                                                    website_answerreference.approval_status = 'A'
                                                    OR website_answerreference.approval_status = 'P'
                                            )
                                    )
                            ) OR (
                                    website_answerreference.approval_status = 'P'
                                    AND (
                                            SELECT
                                                    MAX(create_datetime)
                                            FROM
                                                    website_answerreference AS temp_table
                                            WHERE
                                                    temp_table.question_id = website_answerreference.question_id
                                                    AND temp_table.jurisdiction_id = website_answerreference.jurisdiction_id
                                                    AND temp_table.approval_status = 'A'
                                    ) IS NULL
                            )
                    )
    ORDER BY
            cat_display_order ASC,
            display_order ASC,
            question_id ASC,
            id DESC;
