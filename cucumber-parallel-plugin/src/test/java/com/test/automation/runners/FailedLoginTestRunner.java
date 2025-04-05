package com.test.automation.runners;

import io.cucumber.junit.Cucumber;
import io.cucumber.junit.CucumberOptions;
import org.junit.runner.RunWith;

@RunWith(Cucumber.class)
@CucumberOptions(
        features = "src/test/resources/features/failed_login.feature",
        glue = {"com.test.automation.stepdefinitions", "com.test.automation.hooks"},
        plugin = {
                "pretty",
                "html:target/cucumber-reports/failed-login/cucumber-pretty.html",
                "json:target/cucumber-reports/json/failed-login.json"
        },
        monochrome = true
)
public class FailedLoginTestRunner {
} 