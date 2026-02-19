class NutrientCalculator:
    """
    A class to calculate nutrient values for meals based on the KFCT 2018.
    """

    def __init__(self, food_data: dict) -> None:
        """
        Initialize the NutrientCalculator with food data.
        
        :param food_data: A dictionary containing food items and their nutrient values.
        """
        self.food_data = food_data

    def calculate_meal_nutrients(self, meal_items: list) -> dict:
        """
        Calculate total nutrient values for a list of meal items.
        
        :param meal_items: A list of food items included in the meal.
        :return: A dictionary with total nutrient values.
        """
        total_nutrients = {}
        for item in meal_items:
            nutrients = self.food_data.get(item, {})
            for nutrient, value in nutrients.items():
                total_nutrients[nutrient] = total_nutrients.get(nutrient, 0) + value
        return total_nutrients


class DietaryConditionPlanner:
    """
    A class to provide dietary plans for specific health conditions.
    """

    def __init__(self, condition: str) -> None:
        """
        Initialize the DietaryConditionPlanner with a specific health condition.
        
        :param condition: The health condition for which the dietary plan is created.
        """
        self.condition = condition

    def get_dietary_plan(self) -> str:
        """
        Generate a dietary plan based on the health condition.
        
        :return: A string description of the dietary plan.
        """
        if self.condition == 'type2_diabetes':
            return 'Include high fiber, low glycemic index foods.'
        elif self.condition == 'hypertension':
            return 'Reduce sodium intake and increase potassium-rich foods.'
        elif self.condition == 'anemia':
            return 'Include iron-rich foods along with vitamin C.'
        else:
            return 'Consult a healthcare provider for dietary recommendations.'
