package com.test.automation.hooks;

import com.test.automation.utils.DriverManager;
import io.cucumber.java.After;
import io.cucumber.java.Before;
import io.cucumber.java.Scenario;
import org.openqa.selenium.OutputType;
import org.openqa.selenium.TakesScreenshot;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Duration;

public class Hooks {
    private static final int PAGE_LOAD_TIMEOUT = 30;
    private static final int IMPLICIT_WAIT = 10;

    @Before
    public void setup(Scenario scenario) {
        System.out.println("Starting scenario: " + scenario.getName());
        try {
            WebDriver driver = DriverManager.getDriver();
            driver.manage().timeouts().pageLoadTimeout(Duration.ofSeconds(PAGE_LOAD_TIMEOUT));
            driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(IMPLICIT_WAIT));
            driver.manage().window().maximize();
            driver.manage().deleteAllCookies();
        } catch (Exception e) {
            System.err.println("Error in setup: " + e.getMessage());
            cleanupOnError();
            throw e;
        }
    }

    @After
    public void tearDown(Scenario scenario) {
        try {
            WebDriver driver = DriverManager.getDriver();
            if (scenario.isFailed()) {
                try {
                    byte[] screenshot = ((TakesScreenshot) driver).getScreenshotAs(OutputType.BYTES);
                    scenario.attach(screenshot, "image/png", scenario.getName());
                } catch (Exception e) {
                    System.err.println("Error taking screenshot: " + e.getMessage());
                }
            }
        } finally {
            try {
                Thread.sleep(1000); // Small delay before cleanup
                DriverManager.quitDriver();
            } catch (Exception e) {
                System.err.println("Error in cleanup: " + e.getMessage());
            }
        }
    }

    private void cleanupOnError() {
        try {
            DriverManager.quitDriver();
        } catch (Exception e) {
            System.err.println("Error in error cleanup: " + e.getMessage());
        }
    }
}