INSERT INTO carmate.token (token, expire_at, user_id) VALUES
   (SHA512('token-user-valid'), NOW() + interval '1' day, 1),
   (SHA512('token-admin-valid'), NOW() + interval '1' day, 2),
   (SHA512('token-user-invalid'), NOW() - interval '15' day, 1),
   (SHA512('token-user-banned-valid'), NOW() + interval '1' day, 3),
   (SHA512('token-driver-valid'), NOW() + interval '1' day, 4),
   (SHA512('token-driver-not-validated'), NOW() + interval '1' day, 5);
