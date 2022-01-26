package com.example.payroll;

import java.util.Objects;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;

@Entity
public class Employee {

  private @Id @GeneratedValue Long id;
  private String firstName;
  private String lastName;
  private String description;

  public Employee(String firstName, String lastName, String description) {
    this.firstName = firstName;
    this.lastName = lastName;
    this.description = description;
  }

  @Override
  public boolean equals(Object obj) {
    if (obj == this)
      return true;
    if (!(obj instanceof Employee))
      return false;

    Employee employee = (Employee) obj;
    return Objects.equals(id, employee.id)
        && Objects.equals(firstName, employee.firstName)
        && Objects.equals(lastName, employee.lastName)
        && Objects.equals(description, employee.description);
  }
}
