package com.example.blog

import org.springframework.stereotype.Controller
import org.springframework.ui.Model
import org.springframework.ui.set
import org.springframework.web.bind.annotation.GetMapping

@Controller
class HtmlController {

  @GetMapping("/")
  fun blog(model: Model): String {
    // model.addAttribute("title", "Blog") と同じ
    model["title"] = "Blog"
    return "blog"
  }
}
