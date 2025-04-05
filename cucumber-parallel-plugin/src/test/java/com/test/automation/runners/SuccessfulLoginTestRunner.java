package com.test.automation.runners;

import io.cucumber.junit.Cucumber;
import io.cucumber.junit.CucumberOptions;
import org.junit.runner.RunWith;

@RunWith(Cucumber.class)
@CucumberOptions(
        features = "src/test/resources/features/successful_login.feature",
        glue = {"com.test.automation.stepdefinitions", "com.test.automation.hooks"},
        plugin = {
                "pretty",
                "html:target/cucumber-reports/successful-login/cucumber-pretty.html",
                "json:target/cucumber-reports/json/successful-login.json",
                "rerun:target/failed_scenarios.txt"
        },
        monochrome = true
)
public class SuccessfulLoginTestRunner {
} 