package lk.thiwak.megarunii.browser

import android.app.NotificationManager
import android.content.Context
import android.graphics.Bitmap
import android.util.Log
import android.webkit.*
import android.webkit.WebView
import java.io.InputStream
import java.net.HttpURLConnection
import java.net.URL
import javax.net.ssl.HttpsURLConnection
import javax.net.ssl.SSLContext


open class CustomWebView: WebViewClient() {

    companion object {
        val RAID_SHOOTER_V = 20
        val RAID_SHOOTER_GAME_ID = "9482808f-72c3-43a5-96c4-38c3d3a7673e"
        val FOOD_BLOCKS_V = 24
        val FOOD_BLOCKS_GAME_ID = "907bd637-30c0-435c-af6a-ee2efc4c115a"
        val TAG = "WebUtils"
    }

    private lateinit var requestHeaders: MutableMap<String, List<String>>
    private lateinit var responseHeaders: MutableMap<String, String>

    fun setHeaders(headers: MutableMap<String, List<String>>){
        requestHeaders = headers
    }

    private fun injectHeaders(urlConnection: HttpsURLConnection){
        for ((key, values) in requestHeaders) {
            urlConnection.setRequestProperty(key, values.joinToString(","))
        }
    }

    private fun logResponse(request:HttpsURLConnection, response:WebResourceResponse){
        response.statusCode
        request.url
        request.requestMethod
        request.date

        val text = "${request.requestMethod} ${request.url}\n${request.date}\n${response.statusCode}\n${response.data}"
        Log.d(TAG, text)

    }

    fun openURL(url: String) : WebResourceResponse {

        val urlConnection = (URL(url).openConnection() as HttpsURLConnection).apply {
            sslSocketFactory = SSLContext.getDefault().socketFactory
            injectHeaders(this)
        }
        urlConnection.connect()

        urlConnection.headerFields.forEach { (key, value) ->
            Log.d(TAG, "Header: $key = $value")
        }

        requestHeaders = urlConnection.headerFields

        var response = WebResourceResponse(
            urlConnection.contentType,
            urlConnection.contentEncoding,
            urlConnection.inputStream
        )
        logResponse(urlConnection, response)
        responseHeaders = response.responseHeaders

        return response

    }

}

class MyWebViewClient : CustomWebView() {
    val TAG: String = "WebViewClient"
    //private lateinit var

    val requestHeaders: MutableMap<String, List<String>> = mutableMapOf(
        "User-Agent" to listOf("Custom User-Agent"),
        "Authorization" to listOf("Bearer YOUR_TOKEN"),
        "Accept" to listOf("application/json"),
        "Accept-Encoding" to listOf("gzip", "deflate"),
        "Cookie" to listOf("session=xyz123", "user=abc456")
    )

    override fun shouldOverrideUrlLoading(view: WebView?, url: String?): Boolean {
//        return if (url in blockListedURL) {
//            view?.loadUrl("https//host.that.does.not.exists.and.fuck.wow/home.html")
//            true
//        } else{
//            false
//        }
        return super.shouldOverrideUrlLoading(view, url)
    }

    override fun shouldInterceptRequest(view: WebView?, url: String?): WebResourceResponse? {

        if (url?.startsWith("https://") == true) {
            try {
                return openURL(url)

            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
        return super.shouldInterceptRequest(view, url)
    }

    override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
        if (request?.url?.scheme == "customscheme") {
            // Handle custom scheme
            return true
        }
        return super.shouldOverrideUrlLoading(view, request)
    }

    override fun onPageStarted(view: WebView?, url: String?, favicon: Bitmap?) {
        super.onPageStarted(view, url, favicon)
        Log.d(TAG, "Page started: $url")
        setHeaders(requestHeaders)
    }

    override fun onPageFinished(view: WebView?, url: String?) {
        super.onPageFinished(view, url)
        Log.d(TAG, "Page finished: $url")
    }

    override fun onReceivedError(view: WebView?, request: WebResourceRequest?, error: WebResourceError?) {
        super.onReceivedError(view, request, error)
        view?.loadUrl("file:///android_asset/error.html")
    }
}

class MyWebChromeClient : WebChromeClient() {
    val TAG: String = "WebChromeClient"

    override fun onProgressChanged(view: WebView?, newProgress: Int) {
        super.onProgressChanged(view, newProgress)
        Log.d(TAG, "Loading progress: $newProgress%")
    }

    override fun onReceivedTitle(view: WebView?, title: String?) {
        super.onReceivedTitle(view, title)
        Log.d(TAG, "Page title: $title")
    }

}
