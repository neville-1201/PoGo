import streamlit as st
from functools import lru_cache


# ============================================================
# OPTIMIZER
# ============================================================

def find_max_value(A, B, C, additions, subtractions, T):

    additions = tuple(sorted(set(additions)))
    subtractions = tuple(sorted(set(subtractions)))

    # Display names
    action_names = {
        ("add", 120): "Power Spot",
        ("add", 300): "Exploring",
        ("sub", 250): "Tier 1 Raid",
        ("sub", 400): "Tier 3 Raid",
        ("sub", 800): "Tier 4/5 Raid",
    }

    # --------------------------------------------------------
    # Find all values reachable by subtraction
    # --------------------------------------------------------

    @lru_cache(maxsize=None)
    def subtraction_options(value):

        routes = {value: ()}
        stack = [value]

        while stack:
            current = stack.pop()

            for amount in subtractions:

                new_value = current - amount

                if new_value < 0:
                    continue

                if new_value not in routes:

                    routes[new_value] = (
                        routes[current] + (amount,)
                    )

                    stack.append(new_value)

        return routes


    # --------------------------------------------------------
    # Dynamic programming
    # --------------------------------------------------------

    @lru_cache(maxsize=None)
    def solve(day, value, daily_added):

        # Stop now
        best_value = value
        best_actions = ()
        best_days_used = day

        # ====================================================
        # ADD / SUBTRACT THEN ADD
        # ====================================================

        if daily_added < B:

            reachable = subtraction_options(value)

            for reduced_value, subtraction_sequence in reachable.items():

                # Value must be below C BEFORE addition
                if reduced_value >= C:
                    continue

                for add_amount in additions:

                    new_value = reduced_value + add_amount
                    new_daily_added = daily_added + add_amount

                    (
                        future_value,
                        future_actions,
                        future_days_used
                    ) = solve(
                        day,
                        new_value,
                        new_daily_added
                    )

                    # Prefer higher value.
                    # If same value, prefer fewer days.
                    if (
                        future_value > best_value
                        or (
                            future_value == best_value
                            and future_days_used < best_days_used
                        )
                    ):

                        actions = []
                        temp_value = value

                        # Record subtractions
                        for subtract_amount in subtraction_sequence:

                            temp_value -= subtract_amount

                            actions.append(
                                (
                                    day,
                                    "sub",
                                    subtract_amount,
                                    temp_value,
                                    daily_added
                                )
                            )

                        # Record addition
                        actions.append(
                            (
                                day,
                                "add",
                                add_amount,
                                new_value,
                                new_daily_added
                            )
                        )

                        best_value = future_value
                        best_actions = (
                            tuple(actions)
                            + future_actions
                        )

                        best_days_used = future_days_used


        # ====================================================
        # GO TO NEXT DAY
        # ====================================================

        if day < T:

            (
                future_value,
                future_actions,
                future_days_used
            ) = solve(
                day + 1,
                value,
                0
            )

            # Only choose another day if it actually gives
            # a better result.
            if future_value > best_value:

                best_value = future_value

                best_actions = (
                    (
                        day,
                        "end_day",
                        0,
                        value,
                        daily_added
                    ),
                ) + future_actions

                best_days_used = future_days_used

        return (
            best_value,
            best_actions,
            best_days_used
        )


    max_value, actions, days_used = solve(
        1,
        A,
        0
    )

    return (
        max_value,
        actions,
        days_used,
        action_names
    )


# ============================================================
# STREAMLIT PAGE
# ============================================================

st.set_page_config(
    page_title="Max out Max Particle",
    page_icon="⚡",
    layout="centered"
)

st.title("Max out Max Particle")

st.write(
    """
    Find the best sequence of activities to maximize your
    value within the available number of days.
    """
)


# ============================================================
# STARTING CONDITIONS
# ============================================================

st.header("Starting Conditions")

col1, col2, col3 = st.columns(3)

with col1:

    A = st.number_input(
        "Current Value",
        min_value=0,
        value=0,
        step=10
    )

with col2:

    B = st.number_input(
        "Daily Collection Limit",
        min_value=1,
        value=800,
        step=10
    )

with col3:

    C = st.number_input(
        "Total Limit",
        min_value=1,
        value=1500,
        step=10
    )


# ============================================================
# ADDITIONS
# ============================================================

st.header("Obtain Max Particles")

col1, col2 = st.columns(2)

with col1:

    M = st.number_input(
        "Power Spot",
        min_value=1,
        value=120,
        step=10
    )

with col2:

    N = st.number_input(
        "Exploring",
        min_value=1,
        value=300,
        step=10
    )


# ============================================================
# SUBTRACTIONS
# ============================================================

st.header("Raid Activities")

st.caption(
    "If you cannot access to certain Tier, please change the number to the accessible one."
)

col1, col2, col3 = st.columns(3)

with col1:

    X = st.number_input(
        "Tier 1 Raid Cost",
        min_value=1,
        value=250,
        step=10
    )

with col2:

    Y = st.number_input(
        "Tier 3 Raid Cost",
        min_value=1,
        value=400,
        step=10
    )

with col3:

    Z = st.number_input(
        "Tier 4/5 Raid Cost",
        min_value=1,
        value=800,
        step=10
    )


# ============================================================
# TIME LIMIT
# ============================================================

st.header("Time Limit")

T = st.number_input(
    "Maximum Number of Days (T)",
    min_value=1,
    max_value=100,
    value=1,
    step=1
)


# ============================================================
# CALCULATE
# ============================================================

if st.button(
    "Find Maximum",
    type="primary",
    use_container_width=True
):

    additions = (
        int(M),
        int(N)
    )

    subtractions = (
        int(X),
        int(Y),
        int(Z)
    )

    with st.spinner(
        "Calculating optimal sequence..."
    ):

        (
            max_value,
            actions,
            days_used,
            action_names
        ) = find_max_value(
            int(A),
            int(B),
            int(C),
            additions,
            subtractions,
            int(T)
        )


    # ========================================================
    # RESULT
    # ========================================================

    st.divider()

    st.header("Result")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Maximum Value",
            max_value
        )

    with col2:

        st.metric(
            "Days Used",
            days_used
        )


    # ========================================================
    # OPTIMAL SEQUENCE
    # ========================================================

    st.subheader("Optimal Sequence")

    st.write(
        f"Starting value: **{int(A)}**"
    )

    current_day = None


    for (
        day,
        action_type,
        amount,
        value,
        daily_added
    ) in actions:

        # --------------------------------------------
        # Day heading
        # --------------------------------------------

        if day != current_day:

            st.markdown(
                f"### Day {day}"
            )

            current_day = day


        # --------------------------------------------
        # End day
        # --------------------------------------------

        if action_type == "end_day":

            st.write(
                f"🌙 End Day {day} → **{value}**"
            )

            continue


        # --------------------------------------------
        # ADDITION
        # --------------------------------------------

        if action_type == "add":

            # Get correct display name based on
            # whether this is M or N
            if amount == int(M):
                activity_name = "Power Spot"

            elif amount == int(N):
                activity_name = "Exploring"

            else:
                activity_name = "Addition"

            st.write(
                f"➕ **{activity_name}** "
                f"(+{amount}) → **{value}** "
                f"Daily additions: {daily_added}"
            )


        # --------------------------------------------
        # SUBTRACTION
        # --------------------------------------------

        elif action_type == "sub":

            if amount == int(X):
                activity_name = "Tier 1 Raid"

            elif amount == int(Y):
                activity_name = "Tier 3 Raid"

            elif amount == int(Z):
                activity_name = "Tier 4/5 Raid"

            else:
                activity_name = "Raid"

            st.write(
                f"➖ **{activity_name}** "
                f"(-{amount}) → **{value}**  \n"
                f"Daily additions remain: {daily_added}"
            )


    # ========================================================
    # SUMMARY
    # ========================================================

    total_added = 0
    total_subtracted = 0

    for (
        day,
        action_type,
        amount,
        value,
        daily_added
    ) in actions:

        if action_type == "add":
            total_added += amount

        elif action_type == "sub":
            total_subtracted += amount


    st.divider()

    st.subheader("Summary")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Starting Value",
            int(A)
        )

    with col2:

        st.metric(
            "Final Value",
            max_value
        )

    with col3:

        st.metric(
            "Net Change",
            max_value - int(A)
        )


    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Days Used",
            days_used
        )

    with col2:

        st.metric(
            "Total Added",
            total_added
        )

    with col3:

        st.metric(
            "Total Subtracted",
            total_subtracted
        )
