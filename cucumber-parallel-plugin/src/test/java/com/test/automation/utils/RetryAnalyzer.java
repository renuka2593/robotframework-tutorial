package com.test.automation.utils;

import org.junit.runner.Description;
import org.junit.runners.model.Statement;

public class RetryAnalyzer extends Statement {
    private final Statement base;
    private final Description description;
    private static final int MAX_RETRY = 2;

    public RetryAnalyzer(Statement base, Description description) {
        this.base = base;
        this.description = description;
    }

    @Override
    public void evaluate() throws Throwable {
        Throwable throwable = null;
        
        for (int i = 0; i <= MAX_RETRY; i++) {
            try {
                base.evaluate();
                return; // If successful, return immediately
            } catch (Throwable t) {
                throwable = t;
                System.out.println(
                    String.format("Test '%s' failed on attempt %d of %d",
                        description.getDisplayName(), (i + 1), (MAX_RETRY + 1))
                );
            }
        }
        throw throwable;
    }
} 