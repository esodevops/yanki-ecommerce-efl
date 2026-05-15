# SQL Practice Questions for Yanki E-commerce

Use these real-life business questions to practice SQL data manipulation and reporting with the `yanki` schema (`customers`, `products`, `shipping_address`, `orders`, `payment_method`).

## Questions

1. Which top 10 customers generated the highest total revenue in the last 90 days?
   Difficulty: Easy

2. What are the monthly sales trends (total revenue, total orders, average order value) over the past 12 months?
   Difficulty: Easy

3. Which product categories have the highest and lowest average selling price, and how do they compare to total units sold?
   Difficulty: Easy

4. Identify customers who placed more than 3 orders but have not purchased in the last 60 days (potential churn segment).
   Difficulty: Medium

5. Which states and cities contribute the most revenue, and what is each location's percentage contribution to total sales?
   Difficulty: Medium

6. What is the transaction success rate by payment method, and which method has the highest failure rate?
   Difficulty: Medium

7. Find orders where `Total_Price` does not match `Quantity * Product Price` to detect pricing or ETL anomalies.
   Difficulty: Medium

8. Which products are frequently bought in high quantities (e.g., average quantity per order > 2), and what does that imply for inventory planning?
   Difficulty: Easy

9. For each customer, what is the time gap between their first and most recent purchase, and what is their order frequency per month?
   Difficulty: Hard

10. Build a customer summary report that includes total orders, total spend, average order value, last order date, preferred payment method, and primary shipping country.
    Difficulty: Hard

## Bonus Challenge

Convert Question 10 into a reusable SQL view (for example, `yanki.customer_360_report`) and query it for the top 20 highest-value customers.
Difficulty: Hard
