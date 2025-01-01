package lk.thiwak.megarunii.browser

import android.util.Log
import android.webkit.WebChromeClient
import android.webkit.WebView


class CustomWebChromeClient : WebChromeClient() {

    private val TAG: String = "WebChromeClient"

    // Handle progress change during page loading
    override fun onProgressChanged(view: WebView?, newProgress: Int) {
        super.onProgressChanged(view, newProgress)
        Log.d(TAG, "Loading progress: $newProgress%")
    }

    // Handle page title update
    override fun onReceivedTitle(view: WebView?, title: String?) {
        super.onReceivedTitle(view, title)
        Log.d(TAG, "Page title: $title")
    }
}