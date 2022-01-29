package com.example.blog

import org.springframework.data.repository.CrudRepository

interface UserRepository : CrudRepository<User, Long> {
  fun findByLogin(login: String): User?
}
