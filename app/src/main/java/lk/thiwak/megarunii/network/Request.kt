package lk.thiwak.megarunii.network

import android.content.Context
import lk.thiwak.megarunii.log.Logger
import okhttp3.*
import okhttp3.Request
import okhttp3.HttpUrl.Companion.toHttpUrlOrNull
import java.io.IOException



open class Request(private val context: Context) {

    private var client: OkHttpClient = OkHttpClient.Builder().build()
    private var headers: MutableMap<String, String> = mutableMapOf()


    private fun validateResponse(response: Response): Boolean{
        if (response.code in listOf(201, 200)) {
            return true
        } else if (response.code == 403){
            Logger.error(context, "403:Forbidden")
        } else if (response.code == 401) {
            Logger.error(context,"401:Unauthorized")
            Logger.info(context,"Retry with --update-token")
        } else {
            Logger.debug(context, response.code.toString())
            Logger.error(context,"Unknown")
            Logger.debug(context,response.body.toString())
        }
        return false
    }

    private fun executeRequest(request: Request): Response? {
        return try {
            val response:Response = client.newCall(request).execute()
            if (validateResponse(response)){
                return response
            }
            return null
        } catch (e: IOException) {
            e.printStackTrace()
            null
        }

    }

    private fun buildUrlWithParams(url: String, params: Map<String, String>): String {
        val httpUrl = url.toHttpUrlOrNull()?.newBuilder()
        params.forEach { (key, value) ->
            httpUrl?.addQueryParameter(key, value)
        }
        return httpUrl?.build().toString()
    }

    fun addHeaders(newHeaders: Map<String, String>) {
        headers.putAll(newHeaders)
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

}
