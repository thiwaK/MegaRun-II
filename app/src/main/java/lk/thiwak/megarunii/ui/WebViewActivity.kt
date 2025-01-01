package lk.thiwak.megarunii.ui

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.util.Log
import android.webkit.WebView
import lk.thiwak.megarunii.R
import lk.thiwak.megarunii.browser.MyWebViewClient
import lk.thiwak.megarunii.browser.CustomWebChromeClient


class WebViewActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_web_view)

        val webView = findViewById<WebView>(R.id.webView)
        val webSettings = webView.settings

        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        webView.settings.loadsImagesAutomatically = true
        webView.settings.allowFileAccess = true
        webView.settings.allowContentAccess = true
        //webSettings.loadWithOverviewMode = true
        //webSettings.useWideViewPort = true

        Log.i("##", webSettings.userAgentString)

        val data = mapOf(
            "" to "",
            "referer" to "https://google.com",
            "user-agent" to webSettings.userAgentString,
        )

        webView.webViewClient = MyWebViewClient(this, data)
        webView.webChromeClient = CustomWebChromeClient()

        webView.loadUrl("https://duckduckgo.com/")

    }

}