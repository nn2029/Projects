Intelligent PV Monitoring & Power Efficiency Prediction (ANN)
Applied AI / Machine Learning / IoT Project

📌 Overview
Intelligent PV Monitoring & Power Efficiency Prediction is an applied machine learning project focused on predicting the power efficiency of photovoltaic (PV) systems using artificial neural networks (ANN). The project combines real operational data collected from deployed PV systems with data-driven modeling to estimate power output efficiency and identify potential performance degradation.
The work emphasizes real-world data preprocessing, ANN regression modeling, and performance evaluation, demonstrating how machine learning can be applied to energy systems and IoT-enabled monitoring platforms.

🎯 Project Objectives
* Predict PV system power efficiency using historical inverter and load data
* Apply artificial neural networks to real operational datasets
* Evaluate model performance using standard regression metrics
* Support energy system monitoring through predictive analytics

👨‍💻 My Contribution
This project was developed as a two-person Computer Engineering project. My responsibility focused on the machine learning and data analysis components, including:
* Data preprocessing and feature engineering
* ANN model design and training
* Model evaluation and performance analysis
* Integration of prediction results with a mobile monitoring application

🧠 Model Design
* Model Type: Feed-Forward Backpropagation Neural Network (FFBP)
* Task: Regression (Power Efficiency Prediction)
Architecture
* Input features:
    * Solar power
    * Battery power
    * Load power
* Hidden layers:
    * 2 fully connected layers (256–512 neurons)
* Activation function:
    * ReLU
* Optimizer:
    * Adam (learning rate = 0.001)
* Training:
    * 1000 epochs
    * Validation split applied

📊 Data Processing & Evaluation
Data Processing
* Cleaning and normalization of raw inverter data
* Feature scaling for stable training
* Train–validation split for performance evaluation
Evaluation Metrics
The model was evaluated using multiple regression metrics:
* Mean Squared Error (MSE)
* Mean Absolute Error (MAE)
* Mean Absolute Percentage Error (MAPE)
* R-squared (R²)
* Pearson correlation coefficient
Prediction results were analyzed using:
* Loss curves (training vs validation)
* Predicted vs actual power plots
* Regression scatter plots

🛠 Technology Stack
* Programming Language: Python
* Machine Learning: TensorFlow / Keras, Scikit-learn
* Data Processing: Pandas, NumPy
* Deployment Context: IoT-based PV monitoring system
* Application Layer: Android (Xamarin)

🔍 Why This Project Matters
This project demonstrates the application of machine learning to real-world energy systems, going beyond synthetic datasets or toy examples. It highlights key engineering challenges such as:
* Noisy sensor data
* Feature selection and normalization
* Model convergence and stability
* Interpreting regression performance in operational systems
The work shows how ANN-based models can support predictive maintenance and performance monitoring in renewable energy infrastructure.

⚠️ Limitations & Future Work
* Dataset size limited to available inverter logs
* Evaluation performed on historical data only
* No real-time inference deployment in this version
Planned improvements include:
* Online inference and real-time monitoring
* Larger and more diverse datasets
* Comparison with other regression models
* Model optimization for edge deployment

👤 Author
Nasir Nasir-Ameen B.Eng Computer Engineering
