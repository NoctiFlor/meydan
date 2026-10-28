package com.bahri.meydan;

import android.app.Activity;
import android.content.pm.ApplicationInfo;
import android.os.Bundle;
import android.os.Build;
import android.view.View;
import android.view.KeyEvent;
import android.view.WindowManager;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.window.OnBackInvokedCallback;
import android.window.OnBackInvokedDispatcher;
import java.io.ByteArrayInputStream;
import java.io.IOException;

public final class MainActivity extends Activity {
    private WebView game;
    private static final String ORIGIN = "https://appassets.androidplatform.net";

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        game = new WebView(this);
        if ((getApplicationInfo().flags & ApplicationInfo.FLAG_DEBUGGABLE) != 0) {
            WebView.setWebContentsDebuggingEnabled(true);
        }
        game.setBackgroundColor(0xff172230);
        WebSettings settings = game.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        settings.setMediaPlaybackRequiresUserGesture(true);
        settings.setSupportZoom(false);
        game.setWebChromeClient(new WebChromeClient());
        game.setWebViewClient(new WebViewClient() {
            @Override public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                if ((ORIGIN + "/index.html").equals(request.getUrl().toString())) {
                    try {
                        return new WebResourceResponse("text/html", "UTF-8", getAssets().open("MEYDAN.html"));
                    } catch (IOException e) {
                        return emptyResponse();
                    }
                }
                // The standalone game embeds every model and song. No network is needed.
                if ("https".equals(request.getUrl().getScheme()) || "http".equals(request.getUrl().getScheme())) return emptyResponse();
                return null;
            }
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                return !(ORIGIN + "/index.html").equals(request.getUrl().toString());
            }
        });
        setContentView(game);
        if (Build.VERSION.SDK_INT >= 33) {
            getOnBackInvokedDispatcher().registerOnBackInvokedCallback(
                OnBackInvokedDispatcher.PRIORITY_OVERLAY, new OnBackInvokedCallback() {
                    @Override public void onBackInvoked() { handleBack(); }
                });
        }
        fullscreen();
        game.loadUrl(ORIGIN + "/index.html");
    }

    private static WebResourceResponse emptyResponse() {
        return new WebResourceResponse("text/plain", "UTF-8", new ByteArrayInputStream(new byte[0]));
    }

    private void fullscreen() {
        getWindow().getDecorView().setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY | View.SYSTEM_UI_FLAG_FULLSCREEN |
            View.SYSTEM_UI_FLAG_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
            View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_LAYOUT_STABLE);
    }

    @Override public void onWindowFocusChanged(boolean focus) {
        super.onWindowFocusChanged(focus);
        if (focus) fullscreen();
        else if (game != null) game.evaluateJavascript("window.meydanBackground?.()", null);
    }

    @Override protected void onPause() {
        game.evaluateJavascript("window.meydanBackground?.()", null);
        game.onPause();
        game.pauseTimers();
        super.onPause();
    }

    @Override protected void onResume() {
        super.onResume();
        if (game != null) {
            game.resumeTimers();
            // Reset input before rendering resumes, even if onPause's JS was deferred.
            game.evaluateJavascript("window.meydanForeground?.()", value -> game.onResume());
        }
    }

    @Override public void onBackPressed() {
        handleBack();
    }

    @Override public boolean dispatchKeyEvent(KeyEvent event) {
        // Hardware / three-button Back must not be consumed by WebView history.
        // Gesture navigation uses the OnBackInvokedCallback registered above.
        if (event.getKeyCode() == KeyEvent.KEYCODE_BACK) {
            if (event.getAction() == KeyEvent.ACTION_UP && !event.isCanceled()) handleBack();
            return true;
        }
        return super.dispatchKeyEvent(event);
    }

    private void handleBack() {
        game.evaluateJavascript("window.meydanBack?.()", null);
    }

    @Override protected void onDestroy() {
        game.destroy();
        super.onDestroy();
    }
}
