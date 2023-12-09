INSERT INTO carmate.token (token, expire_at, user_id) VALUES
   (SHA512('token-user-valid'), NOW() + interval '1' day, 1),
   (SHA512('token-admin-valid'), NOW() + interval '1' day, 2),
   (SHA512('token-user-invalid'), NOW() - interval '15' day, 1);
