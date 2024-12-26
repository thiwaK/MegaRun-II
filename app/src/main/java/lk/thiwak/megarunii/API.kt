package lk.thiwak.megarunii

import lk.thiwak.megarunii.Request
import okhttp3.Response
import java.util.logging.Logger



class API(private var AppConfig: Configuration) {

    private val logger = Logger.getLogger(API::class.java.name)

    private var headers:MutableMap<String, String> = mutableMapOf()
    private var request:Request = Request()

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

    private fun get(urlSuffix:String){
        request.addHeaders(headers)
        val response: Response? = request.getData("$BASE_URL/$urlSuffix")
        if (response != null) {
            if
        }
    }

    fun checkout() {
        logger.info(":checkout:")

        headers["authorization"] = "Bearer " + AppConfig.accessToken
        val urlSuffix = "/superapp-common-checkout-service/cart/" + AppConfig.mobileNumber

        request.getData("$BASE_URL/$urlSuffix")
        resp = self.conn.request(
            method = "GET",
            ,
            headers = self.headers
        )

        js = self.validateResponse(resp)
        if js:
            return js

        logger.debug(resp.status_code)
        logger.debug(resp.headers)
        logger.debug(resp.text)
        return None
    }


}