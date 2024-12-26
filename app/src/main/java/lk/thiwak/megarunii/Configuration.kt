package lk.thiwak.megarunii

import java.util.logging.Logger

class Configuration {

    private val logger = Logger.getLogger(API::class.java.name)

    lateinit var xDeviceID: String
    lateinit var accessToken: String
    lateinit var mobileNumber: String
}