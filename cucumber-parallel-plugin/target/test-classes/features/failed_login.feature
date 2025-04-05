Feature: Failed Login to Sauce Demo
  As an invalid user
  I want to see appropriate error messages
  When I try to log in with invalid credentials

  Scenario Outline: Failed login with invalid credentials
    Given I am on the Sauce Demo login page
    When I enter username "<username>"
    And I enter password "<password>"
    And I click the login button
    Then I should see the error message "<error_message>"

    Examples:
      | username        | password     | error_message                                                             |
      | locked_out_user | secret_sauce | Epic sadface: Sorry, this user has been locked out.                       |
      | invalid_user    | secret_sauce | Epic sadface: Username and password do not match any user in this service |
      | standard_user   | wrong_pass   | Epic sadface: Username and password do not match any user in this service |
      |                 | secret_sauce | Epic sadface: Username is required                                        |
      | standard_user   |              | Epic sadface: Password is required                                        |
