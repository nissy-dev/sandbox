package payroll.nonrest;

import java.util.List;
import java.util.stream.Collectors;

import org.springframework.hateoas.CollectionModel;
import org.springframework.hateoas.EntityModel;
import org.springframework.http.ResponseEntity;

// import staticで、staticメソッドをクラス名を指定せずに呼び出すことができる
import static org.springframework.hateoas.server.mvc.WebMvcLinkBuilder.linkTo;
import static org.springframework.hateoas.server.mvc.WebMvcLinkBuilder.methodOn;
import org.springframework.hateoas.IanaLinkRelations;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class EmployeeController {
  private final EmployeeRepository repository;

  private final EmployeeModelAssembler assembler;

  // EmployeeController(EmployeeRepository repository) {
  // this.repository = repository;
  // }

  EmployeeController(EmployeeRepository repository, EmployeeModelAssembler assembler) {
    this.repository = repository;
    this.assembler = assembler;
  }

  // @GetMapping("/employees")
  // List<Employee> all() {
  // return repository.findAll();
  // }
  // @GetMapping("/employees")
  // CollectionModel<EntityModel<Employee>> all() {
  // List<EntityModel<Employee>> employees =
  // repository.findAll().stream().map(employee -> EntityModel.of(employee,
  // linkTo(methodOn(EmployeeController.class).one(employee.getId())).withSelfRel(),
  // linkTo(methodOn(EmployeeController.class).all()).withRel("employees"))).collect(Collectors.toList());
  // return CollectionModel.of(employees,
  // linkTo(methodOn(EmployeeController.class).all()).withSelfRel());
  // }
  // Aggregate root
  // tag::get-aggregate-root[]
  @GetMapping("/employees")
  CollectionModel<EntityModel<Employee>> all() {
    List<EntityModel<Employee>> employees = repository.findAll().stream().map(assembler::toModel)
        .collect(Collectors.toList());
    return CollectionModel.of(employees,
        linkTo(methodOn(EmployeeController.class).all()).withSelfRel());
  }
  // end::get-aggregate-root[]

  // @PostMapping("/employees")
  // Employee newEmployee(@RequestBody Employee newEmployee) {
  // return repository.save(newEmployee);
  // }
  @PostMapping("/employees")
  ResponseEntity<?> newEmployee(@RequestBody Employee newEmployee) { // アノテーションがあることでいい感じにserializeしてくれる
    EntityModel<Employee> entityModel = assembler.toModel(repository.save(newEmployee));
    return ResponseEntity.created(entityModel.getRequiredLink(IanaLinkRelations.SELF).toUri()).body(entityModel);
  }

  // Single item
  // @GetMapping("/employees/{id}")
  // Employee one(@PathVariable Long id) {

  // return repository.findById(id)
  // .orElseThrow(() -> new EmployeeNotFoundException(id));
  // }
  // @GetMapping("/employees/{id}")
  // EntityModel<Employee> one(@PathVariable Long id) {
  // Employee employee = repository.findById(id).orElseThrow(() -> new
  // EmployeeNotFoundException(id));
  // return EntityModel.of(employee,
  // linkTo(methodOn(EmployeeController.class).one(id)).withSelfRel(),
  // linkTo(methodOn(EmployeeController.class).all()).withRel("employees"));
  // }
  @GetMapping("/employees/{id}")
  EntityModel<Employee> one(@PathVariable Long id) {
    Employee employee = repository.findById(id).orElseThrow(() -> new EmployeeNotFoundException(id));
    return assembler.toModel(employee);
  }

  // @PutMapping("/employees/{id}")
  // Employee replaceEmployee(@RequestBody Employee newEmployee, @PathVariable
  // Long id) {
  // return repository.findById(id).map(employee -> {
  // employee.setName(newEmployee.getName());
  // employee.setRole(newEmployee.getRole());
  // return repository.save(employee);
  // }).orElseGet(() -> {
  // newEmployee.setId(id);
  // return repository.save(newEmployee);
  // });
  // }
  @PutMapping("/employees/{id}")
  ResponseEntity<?> replaceEmployee(@RequestBody Employee newEmployee, @PathVariable Long id) {
    Employee updateEmployee = repository.findById(id).map(employee -> {
      employee.setName(newEmployee.getName());
      employee.setRole(newEmployee.getRole());
      return repository.save(employee);
    }).orElseGet(() -> {
      newEmployee.setId(id);
      return repository.save(newEmployee);
    });

    // このままだと常に 201 (created) になるけど、更新の場合は 204 (no content) が適切である
    EntityModel<Employee> entityModel = assembler.toModel(updateEmployee);
    return ResponseEntity.created(entityModel.getRequiredLink(IanaLinkRelations.SELF).toUri()).body(entityModel);
  }

  // @DeleteMapping("/employees/{id}")
  // void deleteEmployee(@PathVariable Long id) {
  // repository.deleteById(id);
  // }
  @DeleteMapping("/employees/{id}")
  ResponseEntity<?> deleteEmployee(@PathVariable Long id) {
    repository.deleteById(id);
    // return 204 (no content) status code
    return ResponseEntity.noContent().build();
  }
}
