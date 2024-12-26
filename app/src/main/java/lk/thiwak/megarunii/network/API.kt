package lk.thiwak.megarunii.network

import okhttp3.Response
import android.content.Context
import lk.thiwak.megarunii.Configuration
import lk.thiwak.megarunii.log.Logger

class API(private var context:Context, private var AppConfig: Configuration) {


    private var headers:MutableMap<String, String> = mutableMapOf()
    private var request: Request = Request(context)

    private val OKHTTP_VER = "4.9.2"
    private val BASE_URL = "https://api.wow.lk"


    init {
        headers.putAll(mapOf(
            "accept" to "application/json, text/plain, */*",
            "accept-encoding" to "gzip",
            "accept-language" to "en",
            "authorization" to "Bearer " + AppConfig.accessToken,
            "content-type" to "application/json",
            "user-agent" to "okhttp/$OKHTTP_VER",
            "x-device-id" to AppConfig.xDeviceID
        ))
    }

    private fun get(urlSuffix:String): String? {
        request.addHeaders(headers)
        val response: Response? = request.getData("$BASE_URL/$urlSuffix")
        if (response != null) {
            return response.body.toString()
        }
        return null
    }

    fun checkout() {
        Logger.info(context, ":checkout:")

        headers["authorization"] = "Bearer " + AppConfig.accessToken
        val urlSuffix = "/superapp-common-checkout-service/cart/" + AppConfig.mobileNumber

        val responseBody = get(urlSuffix)
        //TODO if okay, move to next, if not kill the service

    }


}