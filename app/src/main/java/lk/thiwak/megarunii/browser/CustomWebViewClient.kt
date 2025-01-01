package lk.thiwak.megarunii.browser

import android.util.Log
import android.webkit.WebViewClient
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response

open class CustomWebViewClient : WebViewClient() {

    companion object {
        const val TAG = "CustomWebViewClient"
    }

    private val client = OkHttpClient()

    private fun logResponse(response: Response) {
        val text = """
            ${response.request.method} ${response.request.url}
            ${response.code} ${response.body?.contentType()}
        """.trimIndent()

//        response.headers.forEach { (key, value) ->
//            Log.d(TAG, "Header: $key = $value")
//        }

        Log.d(TAG, text)
    }

    private fun validateRequestHeaders(request: Request){
        request.headers.forEach { (key, value) ->
            Log.d(TAG, "Header: $key = $value")
        }
    }

    fun fetchDataFromUrl(url: String, requestHeaders: Map<String, List<String>>): Response {
        try {
            val request = buildRequest(url, requestHeaders)
            validateRequestHeaders(request)

            val response = client.newCall(request).execute()

            logResponse(response)

            return response
        } catch (e: Exception) {
            Log.e(TAG, "Error fetching data from $url", e)
            throw RuntimeException("Error fetching data", e)
        }
    }

    private fun buildRequest(url: String, requestHeaders: Map<String, List<String>>): Request {
        val builder = Request.Builder()
            .url(url)

        requestHeaders.forEach { (key, values) ->
            if (!key.isNullOrBlank() && !values.isNullOrEmpty()) {
                val headerValue = values.joinToString(",")
                if (headerValue.isNotBlank()) {
                    builder.addHeader(key, headerValue)
//                    Log.d(TAG, "Injected header: $key = $headerValue")
                }
            }
        }

        // Build and return the request
        return builder.build()
    }
}