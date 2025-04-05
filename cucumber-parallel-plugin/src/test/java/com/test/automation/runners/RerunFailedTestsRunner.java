package com.test.automation.runners;

import io.cucumber.junit.Cucumber;
import io.cucumber.junit.CucumberOptions;
import org.junit.runner.RunWith;

@RunWith(Cucumber.class)
@CucumberOptions(
        features = "@target/failed_scenarios.txt",
        glue = {"com.test.automation.stepdefinitions", "com.test.automation.hooks"},
        plugin = {
                "pretty",
                "html:target/cucumber-reports/rerun/cucumber-pretty.html",
                "json:target/cucumber-reports/rerun/json/cucumber.json"
        },
        monochrome = true
)
public class RerunFailedTestsRunner {
} 