package lk.thiwak.megarunii

import android.content.Context
import android.util.Log
import androidx.core.content.ContextCompat
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import lk.thiwak.megarunii.network.Request
import kotlin.properties.Delegates

class Worker(val context: Context): Thread() {

    @Volatile var shouldStop:Boolean = false

    fun stopNow(){
        shouldStop = true

    }

    private fun testNet() {
        val initialHeaders = mapOf(
            "User-Agent" to "OkHTTP",
        )
        val req = Request(context)
        req.addHeaders(initialHeaders)

        val result = req.getData("https://duckduckgo.com", null)

        Log.w("NET", result?.body.toString())
        Log.w("NET", result?.code.toString())
    }

    override fun run() {

        for (i in 1..60) {

            if (shouldStop){
                interrupt()
            }

            if (currentThread().isInterrupted) {
                Log.i("BackgroundService", "Background task interrupted, stopping task...")
                return
            }

            Log.i("BackgroundService", "Task running: $i")

            testNet()

            try {
                sleep(5000)
            } catch (e: InterruptedException) {
                e.printStackTrace()
            }
        }
    }
}