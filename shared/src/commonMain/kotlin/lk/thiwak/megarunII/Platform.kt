package lk.thiwak.megarunII

interface Platform {
    val name: String
}

expect fun getPlatform(): Platform