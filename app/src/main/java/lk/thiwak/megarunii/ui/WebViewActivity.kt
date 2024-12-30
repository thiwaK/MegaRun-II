package lk.thiwak.megarunii.ui

import android.annotation.SuppressLint
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.webkit.WebView
import lk.thiwak.megarunii.R
import lk.thiwak.megarunii.browser.CustomWebView
import lk.thiwak.megarunii.browser.MyWebChromeClient
import lk.thiwak.megarunii.browser.MyWebViewClient
import okhttp3.*
import java.io.IOException


class WebViewActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_web_view)

        val webView = findViewById<WebView>(R.id.webView)
        webView.webViewClient = MyWebViewClient()
        webView.webChromeClient = MyWebChromeClient()

        val webSettings = webView.settings
        webSettings.javaScriptEnabled = true

        webView.loadUrl("https://duckduckgo.com/")

    }

}