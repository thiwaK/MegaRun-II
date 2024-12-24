package lk.thiwak.megarunii.ui.main

import android.provider.Settings
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.Transformations
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import java.util.*
import android.content.Context

class PageViewModel(private val context: Context) : ViewModel() {

    private val _index = MutableLiveData<Int>()
    val text: LiveData<String> = Transformations.map(_index) {

        "This is the UUID"
    }

    fun setIndex(index: Int) {
        _index.value = index
    }
}