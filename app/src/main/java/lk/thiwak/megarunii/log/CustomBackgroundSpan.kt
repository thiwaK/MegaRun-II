package lk.thiwak.megarunii.log

import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.drawable.Drawable
import android.text.Html
import android.text.Spanned
import android.text.style.ReplacementSpan
import android.util.Log

class CustomBackgroundSpan(private val drawable: Drawable) : ReplacementSpan() {

    override fun getSize(
        paint: Paint,
        text: CharSequence,
        start: Int,
        end: Int,
        fm: Paint.FontMetricsInt?
    ): Int {
        // Calculate the width of the text
        return paint.measureText(text, start, end).toInt()
    }

    override fun draw(
        canvas: Canvas,
        text: CharSequence,
        start: Int,
        end: Int,
        x: Float,
        top: Int,
        y: Int,
        bottom: Int,
        paint: Paint
    ) {

        val (date, logLevel, message) = parseLogEntry(text.toString())
        var htmlContent = ""
        if (logLevel == "I") {
            paint.color = Color.CYAN
        } else if (logLevel == "E") {
            paint.color = Color.RED
        } else if (logLevel == "W") {
            paint.color = Color.YELLOW
        } else if (logLevel == "D") {
            paint.color = Color.GRAY
        } else {
            paint.color = Color.GRAY
        }

        val parentWidth = canvas.width.toFloat()

        drawable.setBounds(
            0,  // Align drawable with the left edge of the canvas
            top,
            parentWidth.toInt(), // Align drawable with the right edge of the canvas
            bottom
        )
        drawable.draw(canvas)



        val textPaddingStart = 16f  // Add some padding to the left (optional)
        canvas.drawText(Html.fromHtml(htmlFormatter(text.toString()).toString(), Html.FROM_HTML_MODE_COMPACT), start, end, textPaddingStart, y.toFloat(), paint)
    }



    private fun parseLogEntry(logEntry: String): Triple<String, String, String> {
        val regex = """\[(.*?)\] \[(.*?)\] (.*)""".toRegex()
        val matchResult = regex.matchEntire(logEntry)

        return matchResult?.let {
            val (datetime, level, message) = it.destructured
            Log.i("MM", "$datetime, $level, $message")
            Triple(datetime, level, message)
        } ?:

        return Triple("", "", "")
    }

    private fun htmlFormatter(logEntry: String): Spanned {


        val (datetime, logLevel, message) = parseLogEntry(logEntry)

        var msgTextColor = ""
        var dateTextColor = ""
        var logLevelTextColor = ""

        if (logLevel== "I") {
            msgTextColor = "<font color=#ffffff>"
        } else if (logLevel == "E") {
            msgTextColor = "<font color=#ff0000>"
        } else if (logLevel == "W") {
            msgTextColor = "<font color=#ffff00>"
        } else if (logLevel == "D") {
            msgTextColor = "<font color=#888888>"
        } else {
            msgTextColor = "<font color=#888888>"
        }

        return Html.fromHtml(
            "<p style='margin-bottom:5px; font-size:8px; background-color:#000000; color:#ffffff;'>" +
                    "$msgTextColor[$datetime] [$logLevel]</font>" +
                    " <font color=#ffffff style='font-size:8px;'>$message</font></p>",
            Html.FROM_HTML_MODE_COMPACT
        )




    }

}
