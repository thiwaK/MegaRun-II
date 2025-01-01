package lk.thiwak.megarunii.browser

import android.content.Context
import android.graphics.Bitmap
import android.util.Log
import android.webkit.*


class MyWebViewClient(private val context: Context, private val data: Map<String, String>) : CustomWebViewClient() {

    private val TAG: String = "WebViewClient"
    private val requestHeaders: MutableMap<String, List<String>> = mutableMapOf(
            "sec-ch-ua-platform" to listOf("\"Android\""),
            "X-Requested-With" to listOf("lk.wow.superman"),
            "sec-ch-ua" to listOf(
                "\"Chromium\";v=\"130\"",
                "\"Android WebView\";v=\"130\"",
                "\"Not?A_Brand\";v=\"99\""
            ),
            "Accept-Encoding" to listOf("deflate"),
            "Accept-Language" to listOf("en-GB,en-US;q=0.9,en;q=0.8"),
            "Accept" to listOf("text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"),
        )

    init{
        if (data.containsKey("referer")) {
            requestHeaders["Referer"] = listOf(data["referer"]!!)
        }
        if (data.containsKey("user-agent")) {
            requestHeaders["User-Agent"] = listOf(data["user-agent"]!!)
        }
    }

    override fun shouldInterceptRequest(view: WebView?, url: String?): WebResourceResponse? {

        if (url?.startsWith("https://") == true) {
            try {
                val response = fetchDataFromUrl(url, requestHeaders)
                val contentTypeHeader = response.header("Content-Type", "text/html") ?: "text/html"
                val contentType = contentTypeHeader.split(";")[0].trim() // Take only the content type (before the semicolon)
                val contentEncoding = response.header("Content-Encoding", "UTF-8") // Default to "UTF-8" if not provided
                val statusCode = response.code
                val reasonPhrase = response.message.takeIf { it.isNotBlank() } ?: "OK"
                val responseHeaders = response.headers.toMultimap().mapValues { entry -> entry.value.joinToString(", ") }
                val bodyStream = response.body?.byteStream()

                return WebResourceResponse(
                    contentType,
                    contentEncoding,
                    statusCode,
                    reasonPhrase,
                    responseHeaders,
                    bodyStream
                )

            } catch (e: Exception) {
                // Log the error and handle the failure gracefully
                Log.e(TAG, "Failed to fetch data from $url", e)
            }
        }
        return super.shouldInterceptRequest(view, url)
    }

    override fun onPageStarted(view: WebView?, url: String?, favicon: Bitmap?) {
        super.onPageStarted(view, url, favicon)
        Log.d(TAG, "Page started: $url")
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
