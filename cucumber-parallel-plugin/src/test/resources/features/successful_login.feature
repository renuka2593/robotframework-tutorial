Feature: Successful Login to Sauce Demo
  As a valid user
  I want to log in to Sauce Demo
  So that I can access the products page

  Scenario Outline: Successful login with valid credentials
    Given I am on the Sauce Demo login page
    When I enter username "<username>"
    And I enter password "<password>"
    And I click the login button
    Then I should be redirected to the products page

    Examples:
      | username                | password     |
      | standard_user           | secret_sauce |
      | performance_glitch_user | secret_sauce |
