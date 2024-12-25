package lk.thiwak.megarunii

import okhttp3.*
import okhttp3.Request
import okhttp3.HttpUrl.Companion.toHttpUrlOrNull
import java.io.IOException

class Request {

    private var client: OkHttpClient = OkHttpClient.Builder().build()
    private lateinit var headers: MutableMap<String, String>


    init {
        headers = mutableMapOf(
            "User-Agent" to "OKHTTP"
        )
    }

    private fun buildUrlWithParams(url: String, params: Map<String, String>): String {
        val httpUrl = url.toHttpUrlOrNull()?.newBuilder()
        params.forEach { (key, value) ->
            httpUrl?.addQueryParameter(key, value)
        }
        return httpUrl?.build().toString()
    }

    fun addHeaders(newHeaders: Map<String, String>) {
        if (::headers.isInitialized) {
            headers.putAll(newHeaders)
        } else {
            throw UninitializedPropertyAccessException("Headers not initialized")
        }
    }

    fun getData(url: String, data: Map<String, String>? = null): Response? {
        val finalUrl = data?.let { buildUrlWithParams(url, it) } ?: url
        val requestBuilder = Request.Builder()
            .url(finalUrl)

        headers.forEach { (key, value) ->
            requestBuilder.addHeader(key, value)
        }

        val request = requestBuilder.build()
        return executeRequest(request)
    }

    fun postData(url: String, data: Map<String, String>): Response? {
        val requestBody = FormBody.Builder().apply {
            data.forEach { (key, value) ->
                add(key, value)
            }
        }.build()

        val requestBuilder = Request.Builder()
            .url(url)
            .post(requestBody)

        headers.forEach { (key, value) ->
            requestBuilder.addHeader(key, value)
        }

        val request = requestBuilder.build()
        return executeRequest(request)
    }

    fun putData(url: String, data: Map<String, String>): Response? {
        val requestBody = FormBody.Builder().apply {
            data.forEach { (key, value) ->
                add(key, value)
            }
        }.build()

        val requestBuilder = Request.Builder()
            .url(url)
            .put(requestBody)

        headers.forEach { (key, value) ->
            requestBuilder.addHeader(key, value)
        }

        val request = requestBuilder.build()
        return executeRequest(request)
    }

    private fun executeRequest(request: okhttp3.Request): Response? {
        return try {
            client.newCall(request).execute()
        } catch (e: IOException) {
            e.printStackTrace()
            null
        }
    }
}
