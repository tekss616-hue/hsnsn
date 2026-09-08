from pathlib import Path

java_path = Path('app/src/main/java/com/hsnsn/actiontemplate/MainActivity.java')
manifest_path = Path('app/src/main/AndroidManifest.xml')

java = java_path.read_text(encoding='utf-8')
manifest = manifest_path.read_text(encoding='utf-8')

field_anchor = '    private CredentialManager credentialManager;\n'
fields = '''    private CredentialManager credentialManager;\n    private String pendingUpdateUrl;\n    private int pendingUpdateVersion;\n    private boolean updateDownloadStarted;\n'''
if 'pendingUpdateUrl' not in java:
    if field_anchor not in java:
        raise SystemExit('Updater field anchor not found')
    java = java.replace(field_anchor, fields, 1)

load_anchor = '        webView.loadUrl("file:///android_asset/index.html");\n'
load_replacement = load_anchor + '        new Thread(this::checkForAppUpdate).start();\n'
if 'checkForAppUpdate).start()' not in java:
    if load_anchor not in java:
        raise SystemExit('Updater startup anchor not found')
    java = java.replace(load_anchor, load_replacement, 1)

method_anchor = '    private void ensureFirebaseAuth()'
methods = r'''    private static final String LATEST_RELEASE_API = "https://api.github.com/repos/tekss616-hue/hsnsn/releases/latest";

    private void checkForAppUpdate() {
        java.net.HttpURLConnection connection = null;
        try {
            java.net.URL url = new java.net.URL(LATEST_RELEASE_API);
            connection = (java.net.HttpURLConnection) url.openConnection();
            connection.setConnectTimeout(10000);
            connection.setReadTimeout(10000);
            connection.setRequestProperty("Accept", "application/vnd.github+json");
            connection.setRequestProperty("User-Agent", "HSNSN-Android");
            int response = connection.getResponseCode();
            if (response < 200 || response >= 300) return;
            java.io.BufferedReader reader = new java.io.BufferedReader(new java.io.InputStreamReader(connection.getInputStream(), java.nio.charset.StandardCharsets.UTF_8));
            StringBuilder body = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) body.append(line);
            reader.close();
            JSONObject release = new JSONObject(body.toString());
            String tag = release.optString("tag_name", "");
            java.util.regex.Matcher matcher = java.util.regex.Pattern.compile("(\\d+)").matcher(tag);
            if (!matcher.find()) return;
            int latestCode = Integer.parseInt(matcher.group(1));
            if (latestCode <= BuildConfig.VERSION_CODE) return;
            JSONArray assets = release.optJSONArray("assets");
            if (assets == null) return;
            String apkUrl = "";
            for (int i = 0; i < assets.length(); i++) {
                JSONObject asset = assets.optJSONObject(i);
                if (asset == null) continue;
                String name = asset.optString("name", "");
                if (name.toLowerCase(Locale.ROOT).endsWith(".apk")) {
                    apkUrl = asset.optString("browser_download_url", "");
                    if (!apkUrl.isEmpty()) break;
                }
            }
            if (apkUrl.isEmpty()) return;
            final String foundUrl = apkUrl;
            final int foundCode = latestCode;
            final String foundTag = tag;
            runOnUiThread(() -> showUpdateDialog(foundCode, foundTag, foundUrl));
        } catch (Exception ignored) {
        } finally {
            if (connection != null) connection.disconnect();
        }
    }

    private void showUpdateDialog(int versionCode, String versionName, String apkUrl) {
        if (isFinishing()) return;
        new android.app.AlertDialog.Builder(this)
            .setTitle("تحديث جديد متوفر")
            .setMessage("يتوفر إصدار أحدث من التطبيق (" + versionName + "). اضغط تحديث الآن لتنزيله وتثبيته.")
            .setPositiveButton("تحديث الآن", (dialog, which) -> beginUpdateDownload(versionCode, apkUrl))
            .setNegativeButton("لاحقًا", null)
            .show();
    }

    private void beginUpdateDownload(int versionCode, String apkUrl) {
        pendingUpdateVersion = versionCode;
        pendingUpdateUrl = apkUrl;
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O && !getPackageManager().canRequestPackageInstalls()) {
            try {
                Intent settingsIntent = new Intent(android.provider.Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES,
                    Uri.parse("package:" + getPackageName()));
                startActivity(settingsIntent);
            } catch (Exception ignored) { }
            return;
        }
        if (updateDownloadStarted) return;
        updateDownloadStarted = true;
        try {
            android.app.DownloadManager downloadManager = (android.app.DownloadManager) getSystemService(DOWNLOAD_SERVICE);
            String fileName = "hsnsn-update-" + versionCode + ".apk";
            android.app.DownloadManager.Request request = new android.app.DownloadManager.Request(Uri.parse(apkUrl))
                .setTitle("تحديث التطبيق")
                .setDescription("جارٍ تنزيل الإصدار الجديد...")
                .setNotificationVisibility(android.app.DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
                .setDestinationInExternalFilesDir(this, android.os.Environment.DIRECTORY_DOWNLOADS, fileName);
            final long downloadId = downloadManager.enqueue(request);
            android.content.BroadcastReceiver receiver = new android.content.BroadcastReceiver() {
                @Override public void onReceive(android.content.Context context, Intent intent) {
                    if (intent == null || !android.app.DownloadManager.ACTION_DOWNLOAD_COMPLETE.equals(intent.getAction())) return;
                    if (intent.getLongExtra(android.app.DownloadManager.EXTRA_DOWNLOAD_ID, -1L) != downloadId) return;
                    try { unregisterReceiver(this); } catch (Exception ignored) { }
                    updateDownloadStarted = false;
                    Uri uri = downloadManager.getUriForDownloadedFile(downloadId);
                    if (uri == null) return;
                    try {
                        Intent install = new Intent(Intent.ACTION_VIEW)
                            .setDataAndType(uri, "application/vnd.android.package-archive")
                            .addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_ACTIVITY_NEW_TASK);
                        startActivity(install);
                    } catch (Exception ignored) { }
                }
            };
            android.content.IntentFilter filter = new android.content.IntentFilter(android.app.DownloadManager.ACTION_DOWNLOAD_COMPLETE);
            if (android.os.Build.VERSION.SDK_INT >= 33) registerReceiver(receiver, filter, android.content.Context.RECEIVER_EXPORTED);
            else registerReceiver(receiver, filter);
        } catch (Exception ignored) {
            updateDownloadStarted = false;
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (pendingUpdateUrl != null && !pendingUpdateUrl.isEmpty() && !updateDownloadStarted) {
            if (android.os.Build.VERSION.SDK_INT < android.os.Build.VERSION_CODES.O || getPackageManager().canRequestPackageInstalls()) {
                String url = pendingUpdateUrl;
                int code = pendingUpdateVersion;
                pendingUpdateUrl = null;
                beginUpdateDownload(code, url);
            }
        }
    }

'''
if 'LATEST_RELEASE_API = "https://api.github.com/repos/tekss616-hue/hsnsn/releases/latest"' not in java:
    if method_anchor not in java:
        raise SystemExit('Updater method anchor not found')
    java = java.replace(method_anchor, methods + method_anchor, 1)

permission = '    <uses-permission android:name="android.permission.REQUEST_INSTALL_PACKAGES" />\n'
if 'android.permission.REQUEST_INSTALL_PACKAGES' not in manifest:
    internet = '    <uses-permission android:name="android.permission.INTERNET" />\n'
    if internet not in manifest:
        raise SystemExit('Manifest INTERNET permission anchor not found')
    manifest = manifest.replace(internet, internet + permission, 1)

java_path.write_text(java, encoding='utf-8')
manifest_path.write_text(manifest, encoding='utf-8')
print('Applied in-app GitHub release updater')
