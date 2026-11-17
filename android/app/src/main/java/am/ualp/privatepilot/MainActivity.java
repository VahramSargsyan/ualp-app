package am.ualp.privatepilot;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.CookieManager;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public final class MainActivity extends Activity {
    // Fixed TEST Preview hostname: do not rotate or rebind without owner acceptance.
    private static final String HOST =
        "ualp-app-git-feature-ualp-mvp-006-draft-6b4814-vahram-sargsyan.vercel.app";
    private static final String HOME = "https://" + HOST + "/";
    private WebView page;

    private boolean insideOwnerTest(Uri uri) {
        return "https".equalsIgnoreCase(uri.getScheme())
            && HOST.equalsIgnoreCase(uri.getHost())
            && (uri.getPort() == -1 || uri.getPort() == 443);
    }

    private void openOutside(Uri uri) {
        if (!"https".equalsIgnoreCase(uri.getScheme())) return;
        try {
            startActivity(new Intent(Intent.ACTION_VIEW, uri)
                .addCategory(Intent.CATEGORY_BROWSABLE));
        } catch (ActivityNotFoundException ignored) {
            // Unavailable external browser is not a reason to weaken WebView isolation.
        }
    }

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().setStatusBarColor(Color.rgb(29, 46, 75));
        getWindow().setNavigationBarColor(Color.rgb(23, 32, 47));
        page = new WebView(this);
        page.setBackgroundColor(Color.rgb(243, 246, 250));
        page.setWebChromeClient(new WebChromeClient());

        WebSettings settings = page.getSettings();
        settings.setJavaScriptEnabled(true); // Required by the existing assessment UI.
        settings.setDomStorageEnabled(true); // Optional unfinished draft answers, no credentials.
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(false);
        settings.setJavaScriptCanOpenWindowsAutomatically(false);
        settings.setSupportMultipleWindows(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        settings.setSafeBrowsingEnabled(true);

        CookieManager cookies = CookieManager.getInstance();
        cookies.setAcceptCookie(true);
        cookies.setAcceptThirdPartyCookies(page, false);
        page.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(
                WebView view, WebResourceRequest request) {
                if (!request.isForMainFrame()) return false;
                Uri uri = request.getUrl();
                if (insideOwnerTest(uri)) return false;
                openOutside(uri);
                return true;
            }
            @Override public void onPageFinished(WebView view, String url) {
                CookieManager.getInstance().flush(); // Persist the 30-day HttpOnly cookie.
            }
        });
        setContentView(page);
        // Always navigate in the same app WebView; never use an in-app transient tab.
        page.loadUrl(HOME);
    }

    @Override public void onBackPressed() {
        if (page != null && page.canGoBack()) {
            page.goBack();
        } else {
            // Return to Android launcher; keep the app process/session for next launch.
            moveTaskToBack(true);
        }
    }

    @Override protected void onPause() {
        CookieManager.getInstance().flush();
        super.onPause();
    }

    @Override protected void onDestroy() {
        if (page != null) {
            page.destroy();
            page = null;
        }
        super.onDestroy();
    }
}
