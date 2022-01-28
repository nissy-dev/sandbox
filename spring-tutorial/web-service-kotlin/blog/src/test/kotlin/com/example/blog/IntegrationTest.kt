import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.boot.test.web.client.TestRestTemplate

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class IntegrationTests(@Autowired var restTemplate: TestRestTemplate) {

  @BeforeAll
  fun setup() {
    println(">> Setup")
  }

  @Test
  fun `Assert blog page title, content and status code`() {
    var entity = restTemplate.getForEntity("/", String::class.java)
    assertThat(entity.statusCodeValue).isEqualTo(200)
    assertThat(entity.body).contains("<h1>Blog</h1>")
  }

  @Test
  fun `Assert article page title, content and status code`() {
    println(">> TODO")
  }

  @AfterAll
  fun tearDown() {
    println(">> Tear down")
  }
}
