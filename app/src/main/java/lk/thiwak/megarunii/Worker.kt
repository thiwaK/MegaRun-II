package lk.thiwak.megarunii

import android.util.Log
import kotlin.properties.Delegates

class Worker: Thread() {

    @Volatile var shouldStop:Boolean = false

    fun stopNow(){
        shouldStop = true

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

            try {
                sleep(1000)
            } catch (e: InterruptedException) {
                e.printStackTrace()
            }
        }
    }
}