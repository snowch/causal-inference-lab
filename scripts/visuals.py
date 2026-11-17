"""Teaching diagrams for the lessons that compare causal paths."""

CARDS = {
    'common-causes': (
        'Two paths from training to score',
        ('Treatment path', 'Training → score'),
        ('Common-cause path', 'Training ← preparation → score'),
    ),
    'collider-trap': (
        'Two causes of admission',
        ('One cause', 'Skill → admission'),
        ('The other cause', 'Luck → admission'),
    ),
    'mediator-or-confounder': (
        'Two routes from training to score',
        ('Direct route', 'Training → score'),
        ('Route through practice', 'Training → practice → score'),
    ),
}


def illustration(slug):
    if slug not in CARDS:
        return None
    title, *cards = CARDS[slug]
    return dict(kind='comparison', title=title, cards=cards,
                caption='Arrows show the causal relationships assumed in the example.')
