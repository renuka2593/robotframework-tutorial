package com.test.automation.utils;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.openqa.selenium.firefox.FirefoxOptions;

public class DriverManager {
    private static final ThreadLocal<WebDriver> driver = new ThreadLocal<>();
    private static final String BROWSER = System.getProperty("browser", "chrome").toLowerCase();

    public static WebDriver getDriver() {
        if (driver.get() == null) {
            createDriver();
        }
        return driver.get();
    }

    public static void createDriver() {
        try {
            WebDriver webDriver;
            switch (BROWSER) {
                case "firefox":
                    FirefoxOptions firefoxOptions = new FirefoxOptions();
                    firefoxOptions.addArguments("--start-maximized");
                    webDriver = new FirefoxDriver(firefoxOptions);
                    break;
                default:
                    ChromeOptions options = new ChromeOptions();
                    options.addArguments("--remote-allow-origins=*");
                    options.addArguments("--start-maximized");
                    // Add additional Chrome options for stability
                    options.addArguments("--no-sandbox");
                    options.addArguments("--disable-dev-shm-usage");
                    options.addArguments("--disable-gpu");
                    webDriver = new ChromeDriver(options);
            }
            driver.set(webDriver);
        } catch (Exception e) {
            throw new RuntimeException("Failed to initialize WebDriver: " + e.getMessage());
        }
    }

    public static void quitDriver() {
        try {
            if (driver.get() != null) {
                driver.get().quit();
                driver.remove();
            }
        } catch (Exception e) {
            System.err.println("Error quitting WebDriver: " + e.getMessage());
        }
    }
}