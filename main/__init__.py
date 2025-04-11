import random
import csv
import os

from otree.api import *

doc = """
Two-stage experiment with manager-employee matching
"""

current_dir = os.path.dirname(os.path.abspath(__file__))

class C(BaseConstants):
    NAME_IN_URL = 'main' 
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    PREFER_CHOICES = ['Left', 'Right']
    CHALLENGE_CHOICES = ['NRA', 'Red Cross']
    SURVEY_M_QUESTIONS = [
        'I always pay a lot of attention to how I do things compared with how others do things.',
        'I am not the type of person who compares often with others.',
        'I often compare how I am doing socially (e.g., social skills, popularity) with other people.',
        'I see myself as someone who enjoys winning and hates losing.',
        'I see myself as someone who enjoys competing, regardless of whether I win or lose.',
        'I see myself as a competitive person.',
        'Competition brings the best out of me.',
    ]
    SURVEY_O_QUESTIONS = [
        'I am proud of the contribution to social causes of my organization.',
        'I feel aligned with the values of my organization.',
        'I identify with my organization.',
        'I feel connected to my organization.',
        'I feel comfortable working in my organization.',
        'I feel motivated working in my organization.',
        'I want to stay in my organization.',
    ]
    
    # Path to the CSV file containing manager data
    MANAGER_DATA_PATH = current_dir + '/input.csv'

    # Big5
    CHOICES = range(1, 6)
    QUESTIONS = [
        '...is reserved',
        '...generally trusting',
        '...tends to be lazy',
        '...is relaxed, handles stress well',
        '...has few artistic interests',
        '...does things efficiently',
        '...is outgoing, sociable',
        '...tends to find fault with others',
        '...does a thorough job',
        '...gets nervous easily',
        '...has an active imagination',
        '...perseveres until the task is finished',
    ]

    COMPARISON_QUESTIONS = [
        'I always pay a lot of attention to how I do things compared with how others do things.',
        'I am not the type of person who compares often with others.',
        'I often compare how I am doing socially (e.g., social skills, popularity) with other people.',
        'I see myself as someone who enjoys winning and hates losing.',
        'I see myself as someone who enjoys competing, regardless of whether I win or lose.',
        'I see myself as a competitive person.',
        'Competition brings the best out of me.',
    ]

    DICTATOR_ENDOWMENT = 10

    # Add demographic questions constants
    AGE_LABEL = "What is your age?"
    
    GENDER_LABEL = "What is your gender?"
    GENDER_CHOICES = ["Male", "Female", "Non-binary","Prefer not to say"]
    
    EDUCATION_LABEL = "Please indicate the highest level of education completed"
    EDUCATION_CHOICES = [
        "Less than High School",
        "High School or equivalent",
        "Vocational/Technical School (2 years)",
        "Some College",
        "College Graduate (4 years)",
        "Master's Degree (MA)",
        "Doctoral Degree (PhD)"
    ]

    INCOME_LABEL = "What is your annual household income?"
    INCOME_CHOICES = [
        "Less than $25,000",
        "$25,000 - $49,999",
        "$50,000 - $74,999",
        "$75,000 - $99,999",
        "$100,000 - $149,999",
        "$150,000 or more",
        "Prefer not to say"
    ]
    
    # Demographics - Employment
    EMPLOYMENT_LABEL = "What is your current employment status?"
    EMPLOYMENT_CHOICES = [
        "Full-time employed",
        "Part-time employed",
        "Self-employed",
        "Unemployed",
        "Student",
        "Retired",
        "Unable to work",
        "Other"
    ]
    
    # Demographics - Occupation/Industry
    OCCUPATION_LABEL = "What industry do you work in (or most recently worked in)?"
    OCCUPATION_CHOICES = [
        "Education",
        "Healthcare",
        "Technology/IT",
        "Finance/Banking",
        "Retail/Sales",
        "Manufacturing",
        "Government/Public Service",
        "Arts/Entertainment",
        "Construction/Trades",
        "Transportation/Logistics",
        "Hospitality/Food Service",
        "Legal/Professional Services",
        "Non-profit/NGO",
        "Other"
    ]


class Subsession(BaseSubsession):
    used_manager_ids = models.StringField(initial="")


def creating_session(self:Subsession):
    # Load manager data from CSV using standard library
    if os.path.exists(C.MANAGER_DATA_PATH):
        try:
            # Load the CSV file
            manager_data = []
            header = []
            with open(C.MANAGER_DATA_PATH, 'r', encoding='utf-8-sig') as csvfile:
                csv_reader = csv.reader(csvfile)
                header = next(csv_reader)  # Get header row
                for row in csv_reader:
                    manager_data.append(row)
            # Create a dictionary to map column names to indices
            column_indices = {name: idx for idx, name in enumerate(header)}

            # Store the data in session vars
            self.session.vars['manager_data'] = manager_data
            self.session.vars['manager_data_header'] = header
            self.session.vars['manager_data_columns'] = column_indices
            # Initialize the list of used manager IDs
            self.used_manager_ids = ""
        except Exception as e:
            print(f"Error loading manager data: {e}")
            # Create empty data as fallback
            self.session.vars['manager_data'] = []
            self.session.vars['manager_data_header'] = []
            self.session.vars['manager_data_columns'] = {}
    else:
        print(f"Manager data file not found: {C.MANAGER_DATA_PATH}")
        # Create empty data as fallback
        self.session.vars['manager_data'] = []
        self.session.vars['manager_data_header'] = []
        self.session.vars['manager_data_columns'] = {}


class Group(BaseGroup):
    prefer = models.StringField()
    team = models.StringField()
    organization = models.StringField()
    
    # Fields to store matched manager data
    manager_id = models.StringField()
    manager_prefer = models.StringField()


class Player(BasePlayer):
    # Store the matched manager's ID for reference
    matched_manager_id = models.StringField()
    
    # Store the matched manager's data for reference
    manager_stated_amount = models.StringField()
    manager_correct_amount = models.StringField()
    manager_threshold_integer = models.StringField()

    prefer = models.StringField(
        label="<b>Please select your favorite painting from the options below:</b>",
        choices=C.PREFER_CHOICES,
        widget=widgets.RadioSelectHorizontal
    )
    charity_1 = models.StringField(
        label="1)	Which charity do you identify with?",
        choices=C.CHALLENGE_CHOICES,
        widget=widgets.RadioSelectHorizontal
    )
    charity_2 = models.StringField(
        label="2)	If your organization donates to a charity, which one would you prefer?",
        choices=C.CHALLENGE_CHOICES,
        widget=widgets.RadioSelectHorizontal
    )

    report_rand_int = models.IntegerField()

    report_probability = models.IntegerField(
        label='What is the probability that you will report your manager?',
        min=0,
        max=100,
    )
    report = models.BooleanField()

    SM1 = models.IntegerField(label=C.SURVEY_M_QUESTIONS[0], choices=range(1, 6), widget=widgets.RadioSelectHorizontal)
    SM2 = models.IntegerField(label=C.SURVEY_M_QUESTIONS[1], choices=range(1, 6), widget=widgets.RadioSelectHorizontal)
    SM3 = models.IntegerField(label=C.SURVEY_M_QUESTIONS[2], choices=range(1, 6), widget=widgets.RadioSelectHorizontal)
    SM4 = models.IntegerField(label=C.SURVEY_M_QUESTIONS[3], choices=range(1, 6), widget=widgets.RadioSelectHorizontal)
    SM5 = models.IntegerField(label=C.SURVEY_M_QUESTIONS[4], choices=range(1, 6), widget=widgets.RadioSelectHorizontal)
    SM6 = models.IntegerField(label=C.SURVEY_M_QUESTIONS[5], choices=range(1, 6), widget=widgets.RadioSelectHorizontal)
    SM7 = models.IntegerField(label=C.SURVEY_M_QUESTIONS[6], choices=range(1, 6), widget=widgets.RadioSelectHorizontal)
    
    SO1 = models.IntegerField(label=C.SURVEY_O_QUESTIONS[0], choices=range(1, 6), widget=widgets.RadioSelectHorizontal)
    SO2 = models.IntegerField(label=C.SURVEY_O_QUESTIONS[1], choices=range(1, 6), widget=widgets.RadioSelectHorizontal)
    SO3 = models.IntegerField(label=C.SURVEY_O_QUESTIONS[2], choices=range(1, 6), widget=widgets.RadioSelectHorizontal)
    SO4 = models.IntegerField(label=C.SURVEY_O_QUESTIONS[3], choices=range(1, 6), widget=widgets.RadioSelectHorizontal)
    SO5 = models.IntegerField(label=C.SURVEY_O_QUESTIONS[4], choices=range(1, 6), widget=widgets.RadioSelectHorizontal)
    SO6 = models.IntegerField(label=C.SURVEY_O_QUESTIONS[5], choices=range(1, 6), widget=widgets.RadioSelectHorizontal)
    SO7 = models.IntegerField(label=C.SURVEY_O_QUESTIONS[6], choices=range(1, 6), widget=widgets.RadioSelectHorizontal)
    
    # Big5 questions
    Q1 = models.IntegerField(label=C.QUESTIONS[0], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    Q2 = models.IntegerField(label=C.QUESTIONS[1], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    Q3 = models.IntegerField(label=C.QUESTIONS[2], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    Q4 = models.IntegerField(label=C.QUESTIONS[3], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    Q5 = models.IntegerField(label=C.QUESTIONS[4], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    Q6 = models.IntegerField(label=C.QUESTIONS[5], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    Q7 = models.IntegerField(label=C.QUESTIONS[6], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    Q8 = models.IntegerField(label=C.QUESTIONS[7], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    Q9 = models.IntegerField(label=C.QUESTIONS[8], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    Q10 = models.IntegerField(label=C.QUESTIONS[9], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    Q11 = models.IntegerField(label=C.QUESTIONS[10], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    Q12 = models.IntegerField(label=C.QUESTIONS[11], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    
    # Comparison questions
    Comp1 = models.IntegerField(label=C.COMPARISON_QUESTIONS[0], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    Comp2 = models.IntegerField(label=C.COMPARISON_QUESTIONS[1], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    Comp3 = models.IntegerField(label=C.COMPARISON_QUESTIONS[2], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    Comp4 = models.IntegerField(label=C.COMPARISON_QUESTIONS[3], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    Comp5 = models.IntegerField(label=C.COMPARISON_QUESTIONS[4], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    Comp6 = models.IntegerField(label=C.COMPARISON_QUESTIONS[5], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    Comp7 = models.IntegerField(label=C.COMPARISON_QUESTIONS[6], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    
    # Dictator game
    dictator_keep = models.CurrencyField(
        min=0, 
        max=C.DICTATOR_ENDOWMENT,
        label="(Please move the slider)"
    )
    
    # Demographic fields
    age = models.IntegerField(label=C.AGE_LABEL, min=18, max=100)
    gender = models.StringField(
        label=C.GENDER_LABEL,
        choices=C.GENDER_CHOICES
    )
    education = models.StringField(
        label=C.EDUCATION_LABEL,
        choices=C.EDUCATION_CHOICES
    )
    income = models.StringField(
        label=C.INCOME_LABEL,
        choices=C.INCOME_CHOICES
    )
    employment = models.StringField(
        label=C.EMPLOYMENT_LABEL,
        choices=C.EMPLOYMENT_CHOICES
    )
    occupation = models.StringField(
        label=C.OCCUPATION_LABEL,
        choices=C.OCCUPATION_CHOICES
    )


# Helper functions for working with CSV data
def get_value_from_row(row, column_indices, column_name, default=""):
    """Helper function to get a value from a row using column name"""
    if column_name in column_indices:
        idx = column_indices[column_name]
        if idx < len(row):
            return row[idx]
    return default


# PAGES

class Role(Page):
    @staticmethod
    def before_next_page(player: Player, timeout_happened=False):
        # Match the player with a manager when they first enter the experiment
        subsession = player.subsession
        manager_data = player.session.vars.get('manager_data', [])
        column_indices = player.session.vars.get('manager_data_columns', {})
        
        # If there's no manager data, we can't proceed
        if not manager_data:
            print("Warning: No manager data available for matching")
            return
        
        # Get the list of already used manager IDs
        used_ids = subsession.used_manager_ids.split(',') if subsession.used_manager_ids else []

        # Filter out already used manager IDs
        id_column = column_indices.get('participant.id_in_session', -1)
        if id_column == -1:
            print("Warning: Could not find participant.id_in_session column")
            return
            
        available_managers = [row for row in manager_data 
                             if row[id_column] not in used_ids]
        
        # If no managers are available, we can't proceed
        if not available_managers:
            print("Warning: No available managers for matching")
            return
        
        # Randomly select an available manager
        selected_manager = random.choice(available_managers)
        manager_id = selected_manager[id_column]
        
        # Store the matched manager's ID in player's data
        player.matched_manager_id = manager_id
        
        # Add this manager ID to the used list
        used_ids.append(manager_id)
        subsession.used_manager_ids = ','.join(used_ids)
        
        # Store the manager's preferred painting in the group
        group = player.group
        group.manager_id = manager_id
        
        # Get the manager's preferred painting from the data
        prefer_column = column_indices.get('main.1.player.prefer', -1)
        if prefer_column != -1 and prefer_column < len(selected_manager):
            group.manager_prefer = selected_manager[prefer_column]

            # Set the group's prefer based on the manager's preference
            group.prefer = group.manager_prefer
            
            # Map the preference to a team
            painting_mapping = {
                'Left': 'Klee',
                'Right': 'Kandinsky'
            }
            if group.prefer in painting_mapping:
                group.team = painting_mapping[group.prefer]
            
            # Randomly select an organization
            group.organization = random.choice(C.CHALLENGE_CHOICES)
        
        # Store manager's stated amount and correct amount for later use
        stated_amount_column = column_indices.get('main.1.player.stated_amount', -1)
        correct_amount_column = column_indices.get('main.1.player.briefing_correct_amount', -1)
        threshold_integer_column = column_indices.get('main.1.player.threshold_integer', -1)
        
        if stated_amount_column != -1 and stated_amount_column < len(selected_manager):
            player.manager_stated_amount = selected_manager[stated_amount_column]
        
        if correct_amount_column != -1 and correct_amount_column < len(selected_manager):
            player.manager_correct_amount = selected_manager[correct_amount_column]
            
        # Store the threshold_integer value
        if threshold_integer_column != -1 and threshold_integer_column < len(selected_manager):
            player.manager_threshold_integer = selected_manager[threshold_integer_column]


class Painting(Page):
    form_model = 'player'
    form_fields = ['prefer']
    
    def vars_for_template(self):
        group = self.group
        # Safely access manager_prefer with a default value if it's None
        manager_prefer = group.field_maybe_none('manager_prefer') or 'Not available'
        return {
            'manager_prefer': manager_prefer,
            'team': group.field_maybe_none('team') or 'Not assigned',
            'organization': group.field_maybe_none('organization') or 'Not assigned'
        }
    
    def live_method(self, data):
        group = self.group
        return {self.id_in_group: 'success'}


class GroupInfo(Page):
    def vars_for_template(self):
        group = self.group
        return {
            'team': group.field_maybe_none('team') or 'Not assigned',
            'organization': group.field_maybe_none('organization') or 'Not assigned'
        }


class Charity(Page):
    form_model = 'player'
    form_fields = ['charity_1', 'charity_2']
    
    def vars_for_template(self):
        group = self.group
        return {
            'team': group.field_maybe_none('team') or 'Not assigned',
            'organization': group.field_maybe_none('organization') or 'Not assigned'
        }


class Organization(Page):
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        return {
            'organization': group.field_maybe_none('organization') or 'Not assigned',
            'team': group.field_maybe_none('team') or 'Not assigned'
        }


class MatchingResult(Page):
    def vars_for_template(self):
        group = self.group
        return {
            'team': group.field_maybe_none('team') or 'Not assigned',
            'organization': group.field_maybe_none('organization') or 'Not assigned',
            'player_prefer': self.field_maybe_none('prefer'),
            'group_prefer': group.field_maybe_none('prefer')
        }


class BeforeIQTest(Page):
    def vars_for_template(self):
        group = self.group
        return {
            'team': group.field_maybe_none('team') or 'Not assigned',
            'organization': group.field_maybe_none('organization') or 'Not assigned'
        }


class MisreportingRule2(Page):
    def vars_for_template(self):
        group = self.group
        return {
            'team': group.field_maybe_none('team') or 'Not assigned',
            'organization': group.field_maybe_none('organization') or 'Not assigned',
            'threshold_integer': self.field_maybe_none('manager_threshold_integer') or '8'  # Default to 8 if not found
        }


class Audit(Page):
    form_model = 'player'
    form_fields = ['report_probability']
    
    def vars_for_template(self, timeout_happened=False):
        # Generate a random integer for the reporting mechanism
        self.report_rand_int = random.randint(0, 100)
        
        # Safely get stored manager data with defaults if None
        stated_amount = self.field_maybe_none('manager_stated_amount') or 'Not available'
        correct_amount = self.field_maybe_none('manager_correct_amount') or 'Not available'
        group = self.group
        
        return {
            'stated_amount': stated_amount,
            'correct_amount': correct_amount,
            'manager_id': self.field_maybe_none('matched_manager_id') or 'Not matched',
            'team': group.field_maybe_none('team') or 'Not assigned',
            'organization': group.field_maybe_none('organization') or 'Not assigned'
        }
    
    def before_next_page(self, timeout_happened=False):
        # Determine if the report is successful based on the probability
        if self.report_probability > self.report_rand_int:
            self.report = True
            self.session.vars['report'] = True
        else:
            self.report = False
            self.session.vars['report'] = False


class Survey_m(Page):
    form_model = 'player'
    form_fields = [f'SM{i}' for i in range(1, len(C.SURVEY_M_QUESTIONS) + 1)]
    
    def vars_for_template(self):
        group = self.group
        return {
            'team': group.field_maybe_none('team') or 'Not assigned',
            'organization': group.field_maybe_none('organization') or 'Not assigned',
            'player_prefer': self.field_maybe_none('prefer'),
            'group_prefer': group.field_maybe_none('prefer')
        }


class Survey_o(Page):
    form_model = 'player'
    form_fields = [f'SO{i}' for i in range(1, len(C.SURVEY_O_QUESTIONS) + 1)]
    
    def vars_for_template(self):
        group = self.group
        return {
            'team': group.field_maybe_none('team') or 'Not assigned',
            'organization': group.field_maybe_none('organization') or 'Not assigned'
        }


class Big5(Page):
    form_model = 'player'
    form_fields = [f'Q{i + 1}' for i in range(len(C.QUESTIONS))]


class Comparison(Page):
    form_model = 'player'
    form_fields = [f'Comp{i}' for i in range(1, len(C.COMPARISON_QUESTIONS) + 1)]


class Dictator(Page):
    form_model = 'player'
    form_fields = ['dictator_keep']
    
    def vars_for_template(self):
        return {
            'endowment': C.DICTATOR_ENDOWMENT
        }


class Info(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'education', 'income', 'employment', 'occupation']


class Result(Page):
    def vars_for_template(self):
        report_status = self.session.vars.get('report', False)
        group = self.group
        
        return {
            'manager_id': self.field_maybe_none('matched_manager_id') or 'Not matched',
            'team': group.field_maybe_none('team') or 'Not assigned',
            'organization': group.field_maybe_none('organization') or 'Not assigned',
            'report': report_status,
            'player_payoff': self.payoff
        }


page_sequence = [
    Role,
    Painting,
    MatchingResult,
    Organization,
    BeforeIQTest,
    MisreportingRule2,
    Audit,
    Survey_m,
    Survey_o,
    Big5, 
    Comparison, 
    Dictator, 
    Info, 
    Result
]