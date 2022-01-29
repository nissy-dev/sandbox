package com.example.blog

import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest
import org.springframework.boot.test.autoconfigure.orm.jpa.TestEntityManager

@DataJpaTest
class RepositoriesTest
@Autowired
constructor(
    val entityManager: TestEntityManager,
    val userRepository: UserRepository,
    val articleRepository: ArticleRepository,
) {

  @Test
  fun `When findByIdOrNull then return Article`() {
    // データの登録...?
    var juergen = User("springjuergen", "Juergen", "Hoeller")
    entityManager.persist(juergen)
    var article =
        Article("Spring Framework 5.0 goes GA", "Dear Spring community ...", "Lorem ipsum", juergen)
    entityManager.persist(article)
    entityManager.flush()

    // repository のメソッドをテスト
    var found = articleRepository.findById(article.id!!).orElse(null)
    assertThat(found).isEqualTo(article)
  }

  @Test
  fun `When findByLogin then return User`() {
    val juergen = User("springjuergen", "Juergen", "Hoeller")
    entityManager.persist(juergen)
    entityManager.flush()
    val user = userRepository.findByLogin(juergen.login)
    assertThat(user).isEqualTo(juergen)
  }
}
