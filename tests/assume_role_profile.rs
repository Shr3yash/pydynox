// Credential resolution does not need a Python interpreter or DynamoDB.
#[path = "../src/client_internal/config.rs"]
#[allow(dead_code)]
mod config;

#[path = "../src/client_internal/auth.rs"]
#[allow(dead_code)]
mod auth;

use aws_sdk_dynamodb::config::ProvideCredentials;

#[test]
fn assume_role_source_uses_named_profile() {
    let dir = std::env::temp_dir().join(format!("pydynox-auth-{}", std::process::id()));
    std::fs::create_dir_all(&dir).unwrap();
    let credentials = dir.join("credentials");
    std::fs::write(
        &credentials,
        "[default]\naws_access_key_id = DEFAULTKEY\naws_secret_access_key = default\n\n\
         [source]\naws_access_key_id = SOURCEKEY\naws_secret_access_key = source\n",
    )
    .unwrap();
    let config_file = dir.join("config");
    std::fs::write(&config_file, "[default]\nregion = us-east-1\n").unwrap();

    // SAFETY: this is the only test in this binary, so nothing reads the
    // environment concurrently.
    unsafe {
        std::env::set_var("AWS_SHARED_CREDENTIALS_FILE", &credentials);
        std::env::set_var("AWS_CONFIG_FILE", &config_file);
        std::env::set_var("AWS_ACCESS_KEY_ID", "ENVKEY");
        std::env::set_var("AWS_SECRET_ACCESS_KEY", "env");
    }

    let rt = tokio::runtime::Runtime::new().unwrap();
    let access_key = |profile: Option<&str>| {
        rt.block_on(async {
            auth::assume_role_source_config(profile)
                .await
                .credentials_provider()
                .unwrap()
                .provide_credentials()
                .await
                .map(|c| c.access_key_id().to_string())
        })
    };

    assert_eq!(access_key(Some("source")).unwrap(), "SOURCEKEY");
    assert_eq!(access_key(None).unwrap(), "ENVKEY");
    assert!(access_key(Some("missing")).is_err());

    std::fs::remove_dir_all(&dir).unwrap();
}
