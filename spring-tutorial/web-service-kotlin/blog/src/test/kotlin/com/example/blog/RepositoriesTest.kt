import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.Test
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest
import org.springframework.boot.test.autoconfigure.orm.jpa.TestEntityManager

@DataJpaTest
class RepositoriesTest(
    val entityManager: TestEntityManager,
    val userRepository: UserRepository,
    val articleRepository: ArticleRepository,
) {

  @Test
  fun `When findByIdOrNull then return Article`() {
    var juergen = User("springjuergen", "Juergen", "Hoeller")
    entityManager.persist(juergen)
    var article =
        Article("Spring Framework 5.0 goes GA", "Dear Spring community ...", "Lorem ipsum", juergen)
    entityManager.persist(article)
    entityManager.flush()
    var found = articleRepository.findByIdOrNull(article.id!!)
    assertThat(found).isEqualTo(article)
  }
}
