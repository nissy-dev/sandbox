package com.example.blog

import jakarta.persistence.Entity
import jakarta.persistence.GeneratedValue
import jakarta.persistence.Id

@Entity
class User(
    var login: String = "",
    var firstname: String = "",
    var lastName: String = "",
    var description: String? = null,
    @Id @GeneratedValue var id: Long? = null,
)
