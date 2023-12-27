import matplotlib
matplotlib.use('Agg')

from flask import Flask, render_template, request
from openai import OpenAI
import mysql.connector as sq
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64


app = Flask(__name__)

def sql_translate(text):
    client = OpenAI(api_key="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")
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "mysql SQL table, with property:\n#\n# defect(ID,Defect_Name,Defect_Count)\n#"},
            {"role": "user", "content": f"A query to answer {text}, do not write anything other than the query and always select all columns"}
        ])
    return completion.choices[0].message


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plot', methods=['POST'])
def plot():
    try:
        # Get the user input from the form
        text = request.form.get('query')

        # Rest of the code remains the same as in the previous example
        # MySQL connection setup
        connector = sq.connect(user="mj007", password="Mukundh1703.", host="joyboy2402.mysql.database.azure.com", port=3306, database="defects")
        cursor = connector.cursor()

        # Get the SQL query from OpenAI
        generated_query = sql_translate(text).content
        print("Generated SQL Query:", generated_query)

        # Execute the SQL query
        cursor.execute(generated_query)

        # Fetch the results
        result = cursor.fetchall()

        # Extract data for plotting
        np_array = np.array(result)
        name = np_array[:, 1]
        quantity = np_array[:, 2].astype(int)

        plt.clf()
        # Plotting
        plt.bar(name, quantity, color='blue')
        plt.title(f'{text.title()}')
        plt.xlabel('Defect Name')
        plt.ylabel('Defect Quantity')
        plt.grid(True)

        # Save the plot to a BytesIO object
        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)

        # Encode the image as base64
        img_base64 = base64.b64encode(img.getvalue()).decode()

        # Close the cursor and connection
        cursor.close()
        connector.close()

        # Render the HTML and return it as a response
        return render_template('plot.html', plot_base64=img_base64)

    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(debug=True)
