package com.test.automation.utils;

import io.github.bonigarcia.wdm.WebDriverManager;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;

public class DriverManager {
    private static final ThreadLocal<WebDriver> driverThreadLocal = new ThreadLocal<>();

    public static WebDriver getDriver() {
        if (driverThreadLocal.get() == null) {
            synchronized (DriverManager.class) {
                if (driverThreadLocal.get() == null) {
                    WebDriverManager.chromedriver().setup();
                    ChromeOptions options = new ChromeOptions();
                    options.addArguments(
                        "--remote-allow-origins=*",
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-gpu",
                        "--disable-extensions",
                        "--disable-notifications",
                        "--window-size=1920,1080",
                        "--disable-logging",
                        "--log-level=3",
                        "--silent"
                    );
                    options.setExperimentalOption("useAutomationExtension", false);
                    WebDriver driver = new ChromeDriver(options);
                    driverThreadLocal.set(driver);
                }
            }
        }
        return driverThreadLocal.get();
    }

    public static void quitDriver() {
        WebDriver driver = driverThreadLocal.get();
        if (driver != null) {
            try {
                driver.quit();
            } catch (Exception e) {
                System.err.println("Error quitting WebDriver: " + e.getMessage());
            } finally {
                driverThreadLocal.remove();
            }
        }
    }
} 