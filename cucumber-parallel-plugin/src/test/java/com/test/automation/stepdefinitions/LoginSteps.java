package com.test.automation.stepdefinitions;

import com.test.automation.pages.LoginPage;
import com.test.automation.utils.DriverManager;
import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import org.junit.Assert;

public class LoginSteps {

    private final LoginPage loginPage;

    public LoginSteps() {
        loginPage = new LoginPage(DriverManager.getDriver());
    }

    @Given("I am on the Sauce Demo login page")
    public void iAmOnTheSauceDemoLoginPage() {
        loginPage.navigateToLoginPage();
    }

    @When("I enter username {string}")
    public void iEnterUsername(String username) {
        loginPage.enterUsername(username);
    }

    @When("I enter password {string}")
    public void iEnterPassword(String password) {
        loginPage.enterPassword(password);
    }

    @When("I click the login button")
    public void iClickTheLoginButton() {
        loginPage.clickLoginButton();
    }

    @Then("I should be redirected to the products page")
    public void iShouldBeRedirectedToTheProductsPage() {
        Assert.assertTrue("User should be redirected to products page", loginPage.isOnProductsPage());
    }

    @Then("I should see the error message {string}")
    public void iShouldSeeTheErrorMessage(String expectedError) {
        String actualError = loginPage.getErrorMessage();
        Assert.assertEquals("Error message should match", expectedError, actualError);
    }
} 