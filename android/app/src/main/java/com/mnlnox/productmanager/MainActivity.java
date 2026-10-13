package com.mnlnox.productmanager;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.webkit.CookieManager;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;

public final class MainActivity extends Activity {
    private WebView webView;
    private Uri appOrigin;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().setStatusBarColor(Color.rgb(29, 78, 216));
        getWindow().setNavigationBarColor(Color.BLACK);

        Uri startUri = Uri.parse(BuildConfig.APP_URL);
        if (!"https".equalsIgnoreCase(startUri.getScheme()) || startUri.getHost() == null) {
            Toast.makeText(this, "URL do aplicativo inválida. Gere o APK com uma URL HTTPS.", Toast.LENGTH_LONG).show();
            finish();
            return;
        }
        appOrigin = startUri;

        webView = new WebView(this);
        webView.setBackgroundColor(Color.WHITE);
        webView.getSettings().setJavaScriptEnabled(true);
        webView.getSettings().setDomStorageEnabled(true);
        webView.getSettings().setAllowFileAccess(false);
        webView.getSettings().setAllowContentAccess(false);
        webView.getSettings().setMixedContentMode(android.webkit.WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        CookieManager.getInstance().setAcceptCookie(true);
        CookieManager.getInstance().setAcceptThirdPartyCookies(webView, false);
        webView.setWebChromeClient(new WebChromeClient());
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri uri = request.getUrl();
                if (isAppOrigin(uri)) return false;
                try {
                    startActivity(new Intent(Intent.ACTION_VIEW, uri));
                } catch (Exception ignored) {
                    Toast.makeText(MainActivity.this, "Não foi possível abrir este link.", Toast.LENGTH_SHORT).show();
                }
                return true;
            }
        });
        setContentView(webView);
        if (savedInstanceState == null) {
            webView.loadUrl(startUri.toString());
        } else {
            webView.restoreState(savedInstanceState);
        }
    }

    private boolean isAppOrigin(Uri uri) {
        return uri != null
            && "https".equalsIgnoreCase(uri.getScheme())
            && appOrigin.getHost().equalsIgnoreCase(uri.getHost())
            && effectivePort(uri) == effectivePort(appOrigin);
    }

    private int effectivePort(Uri uri) {
        return uri.getPort() == -1 ? 443 : uri.getPort();
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        if (webView != null) webView.saveState(outState);
        super.onSaveInstanceState(outState);
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }

    @Override
    protected void onDestroy() {
        if (webView != null) {
            webView.destroy();
            webView = null;
        }
        super.onDestroy();
    }
}
