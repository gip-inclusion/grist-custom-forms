const FORM_ID = "eures-beta";
const BASE_PATH = `/forms/${FORM_ID}`;
const LANGS = ["fr", "en", "de"];
const DEFAULT_LANG = "fr";

const copy = {
  fr: {
    common: {
      brandTitle: "EURES beta",
      brandSubtitle: "Mobilité, matching et accompagnement transfrontalier",
      navHome: "Accueil",
      navCandidate: "Candidat",
      navEmployer: "Employeur",
      navStats: "Statistiques",
      langLabel: "Langue",
      partnersLabel: "Partenaires",
      tagsLabel: "Repères",
      footer: "Expérimentation EURES beta pour faciliter la mobilité professionnelle et les recrutements dans la Grande Région.",
      ctaStartCandidate: "Commencer côté candidat",
      ctaStartEmployer: "Commencer côté employeur",
      ctaBackHome: "Retour à l’accueil",
      ctaQuestionnaire: "Démarrer le questionnaire",
      ctaSeeCandidate: "Voir le parcours candidat",
      ctaSeeEmployer: "Voir le parcours employeur",
      matchingTitle: "Comment le matching va fonctionner",
      matchingBullets: [
        "Chaque réponse est envoyée dans GRIST avec un rôle, une langue et un identifiant de reprise.",
        "Un score de compatibilité peut être calculé entre secteurs, mobilité, langues, disponibilités et conditions proposées.",
        "Si le score est élevé, la mise en relation peut être automatisée. Sinon, un contrôle humain peut valider ou corriger."
      ],
      futureTitle: "Ce qui vient ensuite",
      futureBullets: [
        "Tableau de bord candidat pour suivre ses opportunités et son statut.",
        "Tableau de bord employeur pour suivre les profils proposés et les retours.",
        "Historique de matching, validations humaines et traçabilité des décisions."
      ],
      consent: "J’accepte que mes réponses soient utilisées par les équipes et partenaires EURES dans le cadre du matching et de l’accompagnement à la mobilité professionnelle.",
      submit: "Enregistrer mes réponses",
      saving: "Enregistrement en cours...",
      saved: "Réponses enregistrées.",
      saveErrorPrefix: "Échec de l’enregistrement",
      uuidPrefix: "Identifiant de reprise",
      questionnaireNote: "Le questionnaire est volontairement resserré pour cette première version. Il reprend la logique des Tally de référence sans les recopier entièrement.",
      validation: {
        required: "Information obligatoire :",
        invalidEmail: "Adresse e-mail à corriger :",
        invalidValue: "Information à corriger :",
        checkHighlighted: "Vérifiez le champ mis en évidence puis réessayez."
      }
    },
    home: {
      eyebrow: "Une expérimentation dans la Grande Région",
      title: "Faciliter les recrutements et la mobilité professionnelle dans la Grande Région",
      lede: "EURES beta expérimente une nouvelle façon de rapprocher les besoins des employeurs et les projets de mobilité des candidats dans un espace économique transfrontalier.",
      storyTitle: "Un marché du travail transfrontalier encore fragmenté",
      storyText: "Le marché du travail dépasse les frontières nationales, mais les recrutements et les recherches d'emploi restent encore largement organisés pays par pays.\n\nLe projet vise à mieux identifier les besoins, les intentions de mobilité et les opportunités afin de favoriser des mises en relation plus pertinentes et plus rapides.\n\nDans la Grande Région, plusieurs centaines de milliers de personnes travaillent déjà au-delà des frontières. Pourtant, les offres d'emploi et les candidatures circulent encore difficilement entre les pays.\n\nDes employeurs rencontrent des difficultés de recrutement tandis que des candidats ouverts à la mobilité ne repèrent pas toujours les opportunités qui pourraient leur correspondre.",
      statsTitle: "Quelques repères sur la Grande Région",
      stats: [
        ["280 000", "travailleurs frontaliers circulent chaque jour dans la Grande Région."],
        ["40–50 k", "personnes avec expérience transfrontalière pourraient rechercher un emploi."],
        ["15 000+", "postes resteraient vacants dans le même bassin économique."]
      ],
      tracksTitle: "Deux parcours complémentaires",
      candidateTitle: "Parcours candidat",
      candidateText: "Le service permet de mieux comprendre les projets de mobilité, les compétences, les langues et les préférences des personnes afin d'identifier plus facilement les opportunités susceptibles de leur correspondre.",
      employerTitle: "Parcours employeur",
      employerText: "Le service aide à qualifier les besoins de recrutement et à mieux prendre en compte les contraintes et critères importants pour faciliter les mises en relation.",
      principlesTitle: "Une expérimentation centrée sur les usages",
      principles: [
        ["Tester rapidement", "Un premier service léger et multilingue permet de recueillir des besoins réels et d'observer les usages."],
        ["Produire de la connaissance", "Les informations recueillies permettent d'améliorer progressivement la compréhension des besoins des candidats et des employeurs."],
        ["Associer automatisation et expertise humaine", "Le projet explore différentes formes d'assistance tout en conservant la possibilité d'une intervention humaine lorsque cela est nécessaire."]
      ],
      perspectivesTitle: "Perspectives",
      perspectivesBullets: [
        "Ouverture à d'autres pays de la Grande Région.",
        "Intégration de nouveaux secteurs d'activité.",
        "Amélioration continue des parcours utilisateur.",
        "Développement d'outils de suivi et d'accompagnement.",
        "Montée en charge du dispositif à partir des enseignements issus des premiers tests."
      ]
    },
    candidateLanding: {
      kicker: "Parcours candidat",
      title: "Explorez de nouvelles opportunités professionnelles en Europe",
      lede: "Répondez à quelques questions pour nous aider à mieux comprendre votre profil et vos projets de mobilité.",
      messageTitle: "Pourquoi remplir ce questionnaire ?",
      messageIntro: "Si certaines opportunités correspondent à votre expérience, vos compétences et vos préférences, nous pourrons faciliter les mises en relation avec des employeurs qui recrutent.",
      messageBody: [
        "En quelques minutes, vous pouvez préciser votre métier ou votre expérience, les langues que vous maîtrisez, votre disponibilité, votre projet de mobilité et les conditions importantes pour vous.",
        "Que vous souhaitiez travailler au Luxembourg, dans un pays voisin ou envisager une expérience professionnelle ailleurs en Europe, ce service vous aide à identifier des possibilités adaptées à votre situation.",
        "Ces informations nous permettent de mieux identifier les opportunités susceptibles de vous intéresser."
      ],
      messageHighlight: "Vous répondez une seule fois, et votre profil peut ensuite être pris en compte pour différentes opportunités.",
      benefitsTitle: "Ce que le service peut vous apporter",
      benefits: [
        "Découvrir davantage d'opportunités.",
        "Être mis en relation avec des employeurs.",
        "Accéder à un marché de l'emploi plus large.",
        "Construire progressivement votre projet de mobilité."
      ],
      bulletsTitle: "Métiers actuellement testés avec des employeurs luxembourgeois",
      bulletsLead: "Les premiers tests concernent notamment plusieurs secteurs qui recrutent, en particulier avec des employeurs luxembourgeois.",
      bullets: [
        "La vente et le commerce",
        "Le nettoyage et l’entretien",
        "L’hôtellerie et la restauration",
        "L’agriculture et les récoltes",
        "Les missions polyvalentes et les emplois accessibles rapidement"
      ],
      sideTitle: "À propos d'EURES",
      sideText: "EURES est le réseau européen de coopération pour l'emploi. Il accompagne la mobilité professionnelle et facilite les recrutements entre les pays européens.",
      disclaimerTitle: "Ce qui va se passer ensuite",
      disclaimerText: "L'objectif est de vous aider à découvrir des opportunités professionnelles qui correspondent à votre profil et à votre projet de mobilité.",
      processBullets: [
        "1. Analyse du profil.",
        "2. Recherche d'opportunités compatibles.",
        "3. Proposition de mises en relation lorsque des besoins correspondent.",
        "4. Enrichissement progressif du service avec davantage d'employeurs, de pays et de métiers."
      ],
      tags: ["EURES", "France Travail", "Union européenne", "Luxembourg", "Vente & commerce"],
      logos: {
        eures: {
          src: "https://eures.europa.eu/sites/default/files/site-logo-overrides/EURES%20Gradient%20logo%20SVG%20stretched.svg",
          alt: "Logo EURES"
        },
        franceTravail: {
          src: "https://cdn.francetravail.fr/studio/logos/marque/favicon/favicon.svg",
          alt: "Logo France Travail"
        },
        europeanUnion: {
          src: "https://european-union.europa.eu/themes/contrib/oe_theme/dist/eu/images/logo/condensed-version/positive/logo-eu--en.svg",
          alt: "Logo Union européenne"
        }
      }
    },
    employerLanding: {
      kicker: "Parcours employeur",
      title: "Recrutez plus facilement grâce à la mobilité européenne",
      lede: "Décrivez votre besoin de recrutement en quelques minutes et laissez-nous identifier des candidats susceptibles de correspondre à votre recherche, y compris au-delà de votre marché local.",
      messageTitle: "Pourquoi remplir ce questionnaire ?",
      messageIntro: "Ce service s'adresse aux employeurs qui recrutent en transfrontalier ou qui sont prêts à accueillir des candidats venant d'autres pays européens.",
      messageBody: [
        "Le questionnaire permet de mieux comprendre le poste, les compétences recherchées, les langues utiles, les conditions proposées et les besoins éventuels liés à la mobilité.",
        "Notre objectif : vous aider à accéder à un vivier de candidats plus large et faciliter les mises en relation lorsque certains postes sont difficiles à pourvoir.",
        "Plus votre besoin est précis, plus nous sommes en mesure d'identifier des profils compatibles."
      ],
      messageHighlight: "Ce service est conçu pour vous faire gagner du temps et vous aider à élargir votre recherche de candidats quand le recrutement devient plus difficile.",
      benefitsTitle: "Ce que le service peut vous apporter",
      benefits: [
        "Accéder à un vivier de candidats plus large.",
        "Gagner du temps.",
        "Améliorer la qualité des mises en relation.",
        "Être accompagné dans une démarche de recrutement européen."
      ],
      bulletsTitle: "Secteurs particulièrement concernés",
      bulletsLead: "Le service est particulièrement utile lorsque certains recrutements sont difficiles ou lorsque les besoins sont saisonniers ou récurrents.",
      bullets: [
        "La vente et le commerce",
        "Le nettoyage et l’entretien",
        "L’hôtellerie et la restauration",
        "L’agriculture et les récoltes",
        "Les missions polyvalentes et les emplois accessibles rapidement"
      ],
      sideTitle: "Un service simple et utile",
      sideText: "Vous décrivez votre besoin une fois. Nous nous appuyons ensuite sur ces informations pour rechercher des profils pouvant correspondre et faciliter les échanges lorsque cela est pertinent.",
      disclaimerTitle: "Ce qui se passe ensuite",
      disclaimerText: "L'objectif n'est pas de vous faire remplir un formulaire supplémentaire, mais de vous aider à trouver plus facilement les candidats dont vous avez besoin.",
      processBullets: [
        "1. Analyse du besoin.",
        "2. Recherche de profils compatibles.",
        "3. Proposition de mises en relation lorsque des candidats correspondent.",
        "4. Amélioration progressive du service."
      ],
      tags: ["EURES", "France Travail", "Union européenne", "Luxembourg", "Recrutement"]
    },
    candidateQuestionnaire: {
      eyebrow: "Questionnaire candidat",
      title: "Premier signal de matching candidat",
      lede: "Nous captons ici les informations utiles pour vous proposer ensuite des mises en relation ciblées.",
      sections: {
        mobility: "Projet de mobilité",
        profile: "Projet professionnel",
        contact: "Pour vous recontacter"
      },
      fields: {
        residenceCountry: "Pays de résidence",
        targetCountries: "Pays visés",
        mobilityType: "Type de mobilité",
        availability: "Disponibilité de démarrage",
        sectors: "Secteurs recherchés",
        experienceLevel: "Niveau d’expérience",
        languages: "Langues de travail",
        fullName: "Nom complet",
        email: "Adresse e-mail",
        phone: "Téléphone",
        city: "Ville actuelle",
        notes: "Éléments utiles complémentaires"
      },
      options: {
        targetCountries: ["Luxembourg", "France", "Allemagne", "Belgique"],
        mobilityType: ["Transfrontalière", "Expatriation", "Les deux"],
        availability: ["Immédiatement", "Sous 1 mois", "Sous 3 mois", "Plus tard"],
        sectors: ["Vente et commerce", "Nettoyage et entretien", "Hôtellerie-restauration", "Agriculture et récolte", "Missions polyvalentes"],
        experienceLevel: ["Plus de 2 ans", "Entre 6 mois et 2 ans", "Moins de 6 mois", "Débutant mais motivé"],
        languages: ["Français", "Anglais", "Allemand", "Luxembourgeois"]
      },
      helper: "Vous pourrez enrichir ce parcours ensuite avec le CV, les documents administratifs et les critères détaillés par métier."
    },
    employerQuestionnaire: {
      eyebrow: "Questionnaire employeur",
      title: "Premier signal de matching employeur",
      lede: "Nous captons ici les informations utiles pour filtrer et proposer des profils compatibles avec votre besoin.",
      sections: {
        need: "Besoin de recrutement",
        conditions: "Conditions proposées",
        contact: "Pour vous recontacter"
      },
      fields: {
        companyName: "Nom de l’entreprise",
        workLocation: "Lieu de travail",
        sector: "Secteur principal",
        recruitCount: "Nombre de recrutements",
        startDate: "Date ou délai souhaité",
        languagesRequired: "Langues impératives",
        contractDuration: "Durée de contrat",
        weeklyHours: "Volume hebdomadaire",
        installationSupport: "Aides à l’installation",
        criticalCriteria: "Critères indispensables",
        contactName: "Nom du contact",
        email: "Adresse e-mail",
        phone: "Téléphone",
        notes: "Précisions sur le poste"
      },
      options: {
        sector: ["Vente et commerce", "Nettoyage et entretien", "Hôtellerie-restauration", "Agriculture et récolte", "Missions polyvalentes"],
        recruitCount: ["1", "2 à 5", "6 à 10", "10+"],
        languagesRequired: ["Français", "Anglais", "Allemand", "Luxembourgeois"],
        contractDuration: ["Saisonnier", "CDD", "CDI", "À préciser"],
        weeklyHours: ["Temps plein", "Temps partiel", "Variable"],
        installationSupport: ["Aucune aide", "Aide administrative", "Aide logement", "Aide transport"],
        criticalCriteria: ["Disponibilité rapide", "Expérience métier", "Langue orale", "Autonomie", "Mobilité"]
      },
      helper: "Vous pourrez enrichir ensuite le scoring avec les exigences fines par métier et les validations humaines."
    },
    statPage: {
      eyebrow: "Observatoire public de l'expérimentation",
      title: "Suivi de l'expérimentation EURES beta",
      lede: "Cette page présente les principaux indicateurs de suivi de l'expérimentation EURES beta.\n\nLes données publiées sont agrégées et anonymisées. Elles permettent de suivre l'activité du projet et les premiers enseignements issus des usages.",
      updatedPrefix: "Dernière mise à jour",
      methodologyTitle: "Méthodologie",
      methodology: "Les données publiées sont agrégées et anonymisées. Elles permettent de suivre l'activité de l'expérimentation sans afficher de données personnelles.",
      manualNote: "Les indicateurs de suivi du fonctionnement permettent d'observer les mises en relation, les retours et les étapes du parcours.",
      manualMissing: "Les indicateurs de suivi du fonctionnement seront enrichis au fur et à mesure de la montée en charge de l'expérimentation.",
      keyFiguresTitle: "Chiffres clés",
      keyFiguresLead: "Ces premiers résultats permettent d'observer la dynamique de l'expérimentation et les premiers rapprochements entre besoins de recrutement et projets de mobilité.",
      observationsTitle: "Ce que nous observons",
      observationsLead: "Les premiers usages permettent déjà d'identifier les secteurs concernés, les mobilités envisagées et les territoires impliqués.",
      observationsCards: {
        sectors: "Secteurs actuellement représentés",
        mobility: "Mobilité recherchée",
        territories: "Territoires impliqués"
      },
      observationsTexts: {
        sectors: "Les premiers secteurs représentés correspondent aux métiers actuellement explorés dans le cadre de l'expérimentation.",
        mobility: "Les premiers candidats se projettent principalement vers le Luxembourg, dans des parcours transfrontaliers ou vers d'autres pays européens.",
        territories: "Les premiers besoins et projets recensés montrent une dynamique déjà active entre plusieurs pays de la Grande Région et au-delà."
      },
      learningsTitle: "Premiers enseignements",
      learnings: [
        ["Une demande existe", "Les premiers résultats montrent l'existence de besoins de recrutement et l'intérêt de candidats prêts à envisager une mobilité professionnelle."],
        ["Des rapprochements sont possibles", "L'expérimentation permet d'identifier des compatibilités entre les besoins des employeurs et les projets des candidats."],
        ["Une montée en charge progressive", "Le dispositif a vocation à s'enrichir progressivement avec davantage d'employeurs, de secteurs et de territoires."]
      ],
      detailedTitle: "Données détaillées",
      detailedLead: "Les éléments ci-dessous permettent d'approfondir la lecture des usages observés dans le cadre de l'expérimentation.",
      monthlyTitle: "Suivi mensuel",
      monthlyLead: "L'évolution mensuelle permet de suivre la progression du dispositif, l'intensité des usages et les premiers résultats observés.",
      breakdownsTitle: "Répartitions détaillées",
      durationsTitle: "Indicateurs de suivi du fonctionnement",
      hoursUnit: "h",
      daysUnit: "j",
      noDurationData: "n/a",
      totals: {
        candidats: "Candidatures reçues",
        besoins_employeurs: "Besoins employeurs reçus",
        matchings: "Matchings calculés",
        candidats_contactes: "Candidats contactés",
        candidatures_transmises_employeur: "Candidatures transmises",
        contacts_acceptes_employeur: "Contacts acceptés par employeur",
        contacts_refuses_employeur: "Contacts refusés par employeur",
        contacts_sans_reponse_employeur: "Contacts sans réponse employeur",
        embauches: "Embauches"
      },
      monthlyColumns: {
        mois: "Mois",
        candidats: "Candidatures",
        besoins_employeurs: "Besoins employeurs",
        matchings: "Matchings",
        candidats_contactes: "Candidats contactés",
        candidatures_transmises_employeur: "Candidatures transmises",
        contacts_acceptes_employeur: "Acceptés",
        contacts_refuses_employeur: "Refusés",
        contacts_sans_reponse_employeur: "Sans réponse",
        embauches: "Embauches"
      },
      breakdownLabels: {
        besoins_par_pays: "Besoins employeurs par pays",
        secteurs: "Secteurs",
        mobilite_candidats: "Mobilité des candidats",
        experience_internationale_candidats: "Expérience internationale des candidats",
        matchings_par_statut: "Statuts de matching",
        retours_employeurs: "Retours employeurs"
      },
      durationLabels: {
        calcul_to_admin: "Calcul → décision admin",
        admin_to_send: "Décision admin → envoi employeur",
        send_to_employer_response: "Envoi employeur → réponse employeur",
        response_to_relation: "Réponse employeur → mise en relation",
        relation_to_hire: "Mise en relation → embauche"
      },
      durationMetrics: {
        count: "Dossiers mesurés",
        avg: "Délai moyen",
        median: "Délai médian",
        min: "Minimum",
        max: "Maximum"
      },
      emptyBreakdown: "Aucune donnée exploitable pour le moment.",
      loading: "Chargement des statistiques...",
      error: "Impossible de charger les statistiques pour le moment."
    }
  },
  en: {
    common: {
      brandTitle: "EURES beta",
      brandSubtitle: "Cross-border mobility, matching and support",
      navHome: "Home",
      navCandidate: "Candidate",
      navEmployer: "Employer",
      navStats: "Stats",
      langLabel: "Language",
      partnersLabel: "Partners",
      tagsLabel: "Tags",
      footer: "EURES beta experiment to support professional mobility and recruitment across the Greater Region.",
      ctaStartCandidate: "Start as candidate",
      ctaStartEmployer: "Start as employer",
      ctaBackHome: "Back to home",
      ctaQuestionnaire: "Start questionnaire",
      ctaSeeCandidate: "See candidate flow",
      ctaSeeEmployer: "See employer flow",
      matchingTitle: "How matching will work",
      matchingBullets: [
        "Each answer is sent to GRIST with a role, a language and a reusable identifier.",
        "A compatibility score can be computed across sectors, mobility, languages, availability and job conditions.",
        "High scores can trigger automated matching. Lower scores can be reviewed by a human operator."
      ],
      futureTitle: "What comes next",
      futureBullets: [
        "Candidate dashboard to track opportunities and status.",
        "Employer dashboard to track suggested profiles and responses.",
        "Matching history, human validation and decision traceability."
      ],
      consent: "I agree that my answers may be used by EURES teams and partners for matching and mobility support.",
      submit: "Save my answers",
      saving: "Saving...",
      saved: "Answers saved.",
      saveErrorPrefix: "Save failed",
      uuidPrefix: "Resume identifier",
      questionnaireNote: "This questionnaire is intentionally compact for the first version. It follows the logic of the reference Tally forms without copying them in full.",
      validation: {
        required: "Required information:",
        invalidEmail: "Email address to correct:",
        invalidValue: "Information to correct:",
        checkHighlighted: "Check the highlighted field and try again."
      }
    },
    home: {
      eyebrow: "An experiment in the Greater Region",
      title: "Making recruitment and professional mobility easier across the Greater Region",
      lede: "EURES beta is testing a new way to bring together employers' needs and candidates' mobility plans in a cross-border economic area.",
      storyTitle: "A cross-border labour market that remains fragmented",
      storyText: "The labour market goes beyond national borders, yet recruitment and job search are still largely organised country by country.\n\nThe project aims to better identify needs, mobility intentions and opportunities in order to support more relevant and faster introductions.\n\nAcross the Greater Region, several hundred thousand people already work beyond national borders. Even so, job offers and applications still circulate with difficulty between countries.\n\nSome employers face recruitment difficulties, while candidates open to mobility do not always spot the opportunities that could match them.",
      statsTitle: "A few key markers across the Greater Region",
      stats: [
        ["280,000", "cross-border workers commute daily within the Greater Region."],
        ["40–50k", "people with cross-border experience may be looking for work."],
        ["15,000+", "vacancies remain open in the same labour basin."]
      ],
      tracksTitle: "Two complementary paths",
      candidateTitle: "Candidate path",
      candidateText: "The service helps better understand mobility plans, skills, languages and preferences so that relevant opportunities can be identified more easily.",
      employerTitle: "Employer path",
      employerText: "The service helps clarify recruitment needs and better take account of key constraints and criteria in order to support introductions.",
      principlesTitle: "An experiment focused on real uses",
      principles: [
        ["Test quickly", "A first lightweight multilingual service helps collect real needs and observe how people use it."],
        ["Build knowledge", "The information collected helps progressively improve the understanding of candidate and employer needs."],
        ["Combine automation and human expertise", "The project explores different forms of assistance while keeping room for human intervention when needed."]
      ],
      perspectivesTitle: "Perspectives",
      perspectivesBullets: [
        "Opening up to other countries in the Greater Region.",
        "Adding new sectors of activity.",
        "Continuous improvement of user journeys.",
        "Development of follow-up and support tools.",
        "Scaling up the service based on lessons learned from the first tests."
      ]
    },
    candidateLanding: {
      kicker: "Candidate path",
      title: "Explore new professional opportunities in Europe",
      lede: "Answer a few questions to help us better understand your profile and your mobility plans.",
      messageTitle: "Why fill in this questionnaire?",
      messageIntro: "If some opportunities match your experience, skills and preferences, we may help make introductions with employers who are recruiting.",
      messageBody: [
        "In just a few minutes, you can tell us more about your occupation or experience, the languages you speak, your availability, your mobility plans and the conditions that matter to you.",
        "Whether you want to work in Luxembourg, in a neighbouring country or consider a professional experience elsewhere in Europe, this service helps identify possibilities that fit your situation.",
        "This information helps us better identify the opportunities that may interest you."
      ],
      messageHighlight: "You answer once, and your profile can then be considered for different opportunities.",
      benefitsTitle: "What the service can bring you",
      benefits: [
        "Discover more opportunities.",
        "Be connected with employers.",
        "Access a wider labour market.",
        "Build your mobility project progressively."
      ],
      bulletsTitle: "Jobs currently tested with employers in Luxembourg",
      bulletsLead: "The first tests currently focus on several recruiting sectors, especially with employers based in Luxembourg.",
      bullets: [
        "Retail and sales",
        "Cleaning and maintenance",
        "Hospitality and food service",
        "Agriculture and harvesting",
        "Flexible jobs and roles accessible quickly"
      ],
      sideTitle: "About EURES",
      sideText: "EURES is the European employment cooperation network. It supports professional mobility and helps recruitment across European countries.",
      disclaimerTitle: "What happens next",
      disclaimerText: "The goal is to help you discover professional opportunities that match your profile and your mobility plans.",
      processBullets: [
        "1. Review of the profile.",
        "2. Search for compatible opportunities.",
        "3. Suggested introductions when needs match.",
        "4. Progressive expansion of the service with more employers, countries and occupations."
      ],
      tags: ["EURES", "France Travail", "European Union", "Luxembourg", "Retail & sales"],
      logos: {
        eures: {
          src: "https://eures.europa.eu/sites/default/files/site-logo-overrides/EURES%20Gradient%20logo%20SVG%20stretched.svg",
          alt: "EURES logo"
        },
        franceTravail: {
          src: "https://cdn.francetravail.fr/studio/logos/marque/favicon/favicon.svg",
          alt: "France Travail logo"
        },
        europeanUnion: {
          src: "https://european-union.europa.eu/themes/contrib/oe_theme/dist/eu/images/logo/condensed-version/positive/logo-eu--en.svg",
          alt: "European Union logo"
        }
      }
    },
    employerLanding: {
      kicker: "Employer path",
      title: "Recruit more easily thanks to European mobility",
      lede: "Describe your recruitment need in just a few minutes and let us identify candidates who may match your search, including beyond your local labour market.",
      messageTitle: "Why fill in this questionnaire?",
      messageIntro: "This service is for employers recruiting across borders or willing to welcome candidates coming from other European countries.",
      messageBody: [
        "The questionnaire helps us better understand the role, the skills required, the useful languages, the conditions offered and any needs related to mobility.",
        "Our goal is to help you access a wider pool of candidates and support introductions when some vacancies are difficult to fill.",
        "The more precise your need is, the better we can identify compatible profiles."
      ],
      messageHighlight: "This service is designed to save you time and help you widen your search for candidates when recruitment becomes more difficult.",
      benefitsTitle: "What the service can bring you",
      benefits: [
        "Access a wider pool of candidates.",
        "Save time.",
        "Improve the quality of introductions.",
        "Be supported in a European recruitment approach."
      ],
      bulletsTitle: "Sectors especially concerned",
      bulletsLead: "The service is especially useful when some recruitments are difficult or when needs are seasonal or recurrent.",
      bullets: [
        "Sales and retail",
        "Cleaning and maintenance",
        "Hospitality and food service",
        "Agriculture and harvesting",
        "Versatile jobs and roles accessible quickly"
      ],
      sideTitle: "A simple and useful service",
      sideText: "You describe your need once. We then rely on this information to look for profiles that may match and to facilitate exchanges when relevant.",
      disclaimerTitle: "What happens next",
      disclaimerText: "The goal is not to make you fill in one more form, but to help you find the candidates you need more easily.",
      processBullets: [
        "1. Review of the need.",
        "2. Search for compatible profiles.",
        "3. Suggested introductions when candidates match.",
        "4. Progressive improvement of the service."
      ],
      tags: ["EURES", "France Travail", "European Union", "Luxembourg", "Recruitment"]
    },
    candidateQuestionnaire: {
      eyebrow: "Candidate questionnaire",
      title: "First candidate matching signal",
      lede: "We capture the minimum useful information to propose relevant introductions later.",
      sections: {
        mobility: "Mobility plan",
        profile: "Professional profile",
        contact: "Contact details"
      },
      fields: {
        residenceCountry: "Country of residence",
        targetCountries: "Target countries",
        mobilityType: "Mobility type",
        availability: "Availability",
        sectors: "Target sectors",
        experienceLevel: "Experience level",
        languages: "Working languages",
        fullName: "Full name",
        email: "Email",
        phone: "Phone",
        city: "Current city",
        notes: "Additional context"
      },
      options: {
        targetCountries: ["Luxembourg", "France", "Germany", "Belgium"],
        mobilityType: ["Cross-border", "Relocation", "Both"],
        availability: ["Immediately", "Within 1 month", "Within 3 months", "Later"],
        sectors: ["Retail and sales", "Cleaning and maintenance", "Hospitality", "Agriculture and harvest", "Flexible entry jobs"],
        experienceLevel: ["More than 2 years", "6 months to 2 years", "Less than 6 months", "Beginner but motivated"],
        languages: ["French", "English", "German", "Luxembourgish"]
      },
      helper: "You can extend this later with CV upload, admin documents and detailed criteria by sector."
    },
    employerQuestionnaire: {
      eyebrow: "Employer questionnaire",
      title: "First employer matching signal",
      lede: "We capture the minimum useful information to filter and suggest compatible profiles.",
      sections: {
        need: "Hiring need",
        conditions: "Conditions offered",
        contact: "Contact details"
      },
      fields: {
        companyName: "Company name",
        workLocation: "Work location",
        sector: "Main sector",
        recruitCount: "Hiring volume",
        startDate: "Start date or timing",
        languagesRequired: "Required languages",
        contractDuration: "Contract duration",
        weeklyHours: "Weekly workload",
        installationSupport: "Relocation support",
        criticalCriteria: "Critical criteria",
        contactName: "Contact name",
        email: "Email",
        phone: "Phone",
        notes: "Role details"
      },
      options: {
        sector: ["Retail and sales", "Cleaning and maintenance", "Hospitality", "Agriculture and harvest", "Flexible entry jobs"],
        recruitCount: ["1", "2 to 5", "6 to 10", "10+"],
        languagesRequired: ["French", "English", "German", "Luxembourgish"],
        contractDuration: ["Seasonal", "Fixed-term", "Permanent", "To be defined"],
        weeklyHours: ["Full-time", "Part-time", "Variable"],
        installationSupport: ["No support", "Administrative support", "Housing support", "Transport support"],
        criticalCriteria: ["Fast availability", "Sector experience", "Spoken language", "Autonomy", "Mobility"]
      },
      helper: "You can extend the scoring later with detailed requirements per sector and human validation."
    },
    statPage: {
      eyebrow: "Public observatory of the experiment",
      title: "Tracking the EURES beta experiment",
      lede: "This page presents the main monitoring indicators for the EURES beta experiment.\n\nPublished data is aggregated and anonymized. It helps track project activity and the first lessons emerging from use.",
      updatedPrefix: "Last updated",
      methodologyTitle: "Methodology",
      methodology: "Published data is aggregated and anonymized. It helps monitor the experiment without displaying personal data.",
      manualNote: "Operational follow-up indicators help observe introductions, feedback and the main steps of the journey.",
      manualMissing: "Operational follow-up indicators will be expanded as the experiment scales up.",
      keyFiguresTitle: "Key figures",
      keyFiguresLead: "These first results help show the momentum of the experiment and the first links between hiring needs and mobility plans.",
      observationsTitle: "What we are observing",
      observationsLead: "Early usage already highlights represented sectors, mobility patterns and involved territories.",
      observationsCards: {
        sectors: "Sectors currently represented",
        mobility: "Mobility sought",
        territories: "Territories involved"
      },
      observationsTexts: {
        sectors: "The first represented sectors reflect the occupations currently explored in the experiment.",
        mobility: "The first candidates mainly project themselves towards Luxembourg, through cross-border paths or other European destinations.",
        territories: "The first needs and candidate plans already show an active dynamic between several countries in the Greater Region and beyond."
      },
      learningsTitle: "First lessons",
      learnings: [
        ["There is demand", "The first results show both hiring needs and interest from candidates willing to consider professional mobility."],
        ["Matches are possible", "The experiment helps identify compatibilities between employer needs and candidate plans."],
        ["A gradual scale-up", "The approach is designed to expand progressively with more employers, sectors and territories."]
      ],
      detailedTitle: "Detailed data",
      detailedLead: "The sections below provide a more detailed view of usage patterns observed through the experiment.",
      monthlyTitle: "Monthly tracking",
      monthlyLead: "Monthly trends help track the rollout of the service, the level of usage and the first observed results.",
      breakdownsTitle: "Detailed breakdowns",
      durationsTitle: "Operational follow-up indicators",
      hoursUnit: "h",
      daysUnit: "d",
      noDurationData: "n/a",
      totals: {
        candidats: "Candidate submissions",
        besoins_employeurs: "Employer needs",
        matchings: "Computed matchings",
        candidats_contactes: "Candidates contacted",
        candidatures_transmises_employeur: "Applications transmitted",
        contacts_acceptes_employeur: "Employer-accepted contacts",
        contacts_refuses_employeur: "Employer refusals",
        contacts_sans_reponse_employeur: "No employer response",
        embauches: "Hires"
      },
      monthlyColumns: {
        mois: "Month",
        candidats: "Candidates",
        besoins_employeurs: "Employer needs",
        matchings: "Matchings",
        candidats_contactes: "Candidates contacted",
        candidatures_transmises_employeur: "Applications transmitted",
        contacts_acceptes_employeur: "Accepted",
        contacts_refuses_employeur: "Refused",
        contacts_sans_reponse_employeur: "No response",
        embauches: "Hires"
      },
      breakdownLabels: {
        besoins_par_pays: "Employer needs by country",
        secteurs: "Sectors",
        mobilite_candidats: "Candidate mobility",
        experience_internationale_candidats: "Candidates' international experience",
        matchings_par_statut: "Matching statuses",
        retours_employeurs: "Employer feedback"
      },
      durationLabels: {
        calcul_to_admin: "Scoring → admin decision",
        admin_to_send: "Admin decision → employer send",
        send_to_employer_response: "Employer send → employer response",
        response_to_relation: "Employer response → introduction",
        relation_to_hire: "Introduction → hire"
      },
      durationMetrics: {
        count: "Measured cases",
        avg: "Average",
        median: "Median",
        min: "Minimum",
        max: "Maximum"
      },
      emptyBreakdown: "No usable data yet.",
      loading: "Loading statistics...",
      error: "Unable to load statistics right now."
    }
  },
  de: {
    common: {
      brandTitle: "EURES beta",
      brandSubtitle: "Grenzüberschreitende Mobilität, Matching und Begleitung",
      navHome: "Start",
      navCandidate: "Kandidaten",
      navEmployer: "Arbeitgeber",
      navStats: "Statistik",
      langLabel: "Sprache",
      partnersLabel: "Partner",
      tagsLabel: "Stichworte",
      footer: "EURES-beta-Experiment zur Unterstützung beruflicher Mobilität und Rekrutierung in der Großregion.",
      ctaStartCandidate: "Als Kandidat starten",
      ctaStartEmployer: "Als Arbeitgeber starten",
      ctaBackHome: "Zur Startseite",
      ctaQuestionnaire: "Fragebogen starten",
      ctaSeeCandidate: "Kandidatenweg ansehen",
      ctaSeeEmployer: "Arbeitgeberweg ansehen",
      matchingTitle: "So soll das Matching funktionieren",
      matchingBullets: [
        "Jede Antwort wird mit Rolle, Sprache und Wiederaufnahme-ID in GRIST gespeichert.",
        "Ein Kompatibilitätsscore kann aus Branche, Mobilität, Sprachen, Verfügbarkeit und Arbeitsbedingungen berechnet werden.",
        "Hohe Scores können automatisch gematcht werden. Niedrige Scores gehen in eine menschliche Prüfung."
      ],
      futureTitle: "Nächste Ausbaustufen",
      futureBullets: [
        "Kandidaten-Dashboard für Chancen und Status.",
        "Arbeitgeber-Dashboard für vorgeschlagene Profile und Rückmeldungen.",
        "Matching-Historie, menschliche Freigaben und nachvollziehbare Entscheidungen."
      ],
      consent: "Ich stimme zu, dass meine Antworten von EURES-Teams und Partnern für Matching und Mobilitätsbegleitung verwendet werden.",
      submit: "Meine Antworten speichern",
      saving: "Speicherung läuft...",
      saved: "Antworten gespeichert.",
      saveErrorPrefix: "Speichern fehlgeschlagen",
      uuidPrefix: "Wiederaufnahme-ID",
      questionnaireNote: "Dieser Fragebogen ist für die erste Version bewusst kompakt. Er orientiert sich an den vorhandenen Tally-Formularen, ohne sie vollständig zu kopieren.",
      validation: {
        required: "Pflichtangabe:",
        invalidEmail: "E-Mail-Adresse bitte korrigieren:",
        invalidValue: "Angabe bitte korrigieren:",
        checkHighlighted: "Bitte prüfen Sie das markierte Feld und versuchen Sie es erneut."
      }
    },
    home: {
      eyebrow: "Ein Experiment in der Großregion",
      title: "Rekrutierung und berufliche Mobilität in der Großregion erleichtern",
      lede: "EURES beta erprobt einen neuen Weg, um den Bedarf von Arbeitgebern und die Mobilitätspläne von Kandidatinnen und Kandidaten in einem grenzüberschreitenden Wirtschaftsraum besser zusammenzubringen.",
      storyTitle: "Ein grenzüberschreitender Arbeitsmarkt, der noch immer fragmentiert ist",
      storyText: "Der Arbeitsmarkt geht über nationale Grenzen hinaus, doch Stellensuche und Rekrutierung sind noch immer weitgehend von Land zu Land organisiert.\n\nDas Projekt soll Bedarfe, Mobilitätsabsichten und Chancen besser sichtbar machen, um passendere und schnellere Vermittlungen zu ermöglichen.\n\nIn der Großregion arbeiten bereits mehrere hunderttausend Menschen jenseits nationaler Grenzen. Trotzdem zirkulieren Stellenangebote und Bewerbungen noch immer nur schwer zwischen den Ländern.\n\nEinige Arbeitgeber haben Rekrutierungsschwierigkeiten, während mobilitätsbereite Kandidatinnen und Kandidaten passende Chancen nicht immer erkennen.",
      statsTitle: "Einige Orientierungspunkte in der Großregion",
      stats: [
        ["280.000", "Grenzpendler bewegen sich täglich in der Großregion."],
        ["40–50 Tsd.", "Menschen mit grenzüberschreitender Erfahrung könnten Arbeit suchen."],
        ["15.000+", "offene Stellen bleiben im selben Arbeitsraum unbesetzt."]
      ],
      tracksTitle: "Zwei ergänzende Wege",
      candidateTitle: "Kandidatenpfad",
      candidateText: "Der Dienst hilft dabei, Mobilitätspläne, Kompetenzen, Sprachen und Präferenzen besser zu verstehen, damit passende Chancen leichter erkannt werden können.",
      employerTitle: "Arbeitgeberpfad",
      employerText: "Der Dienst hilft dabei, Personalbedarfe zu präzisieren und wichtige Rahmenbedingungen und Kriterien besser zu berücksichtigen, um Vermittlungen zu erleichtern.",
      principlesTitle: "Ein Experiment mit Fokus auf reale Nutzung",
      principles: [
        ["Schnell testen", "Ein erster leichter und mehrsprachiger Dienst hilft dabei, reale Bedarfe zu sammeln und Nutzungen zu beobachten."],
        ["Wissen aufbauen", "Die gesammelten Informationen helfen dabei, das Verständnis der Bedarfe von Kandidatinnen, Kandidaten und Arbeitgebern schrittweise zu verbessern."],
        ["Automatisierung und menschliche Expertise verbinden", "Das Projekt erprobt verschiedene Formen der Unterstützung und lässt zugleich Raum für menschliches Eingreifen, wenn es nötig ist."]
      ],
      perspectivesTitle: "Perspektiven",
      perspectivesBullets: [
        "Öffnung für weitere Länder der Großregion.",
        "Einbeziehung neuer Tätigkeitsbereiche.",
        "Kontinuierliche Verbesserung der Nutzerwege.",
        "Entwicklung von Werkzeugen für Begleitung und Nachverfolgung.",
        "Schrittweise Skalierung auf Basis der Erkenntnisse aus den ersten Tests."
      ]
    },
    candidateLanding: {
      kicker: "Kandidatenpfad",
      title: "Neue berufliche Chancen in Europa entdecken",
      lede: "Beantworten Sie einige Fragen, damit wir Ihr Profil und Ihre Mobilitätspläne besser verstehen können.",
      messageTitle: "Warum diesen Fragebogen ausfüllen?",
      messageIntro: "Wenn einige Chancen zu Ihrer Erfahrung, Ihren Kompetenzen und Ihren Präferenzen passen, können wir Vermittlungen mit rekrutierenden Arbeitgebern erleichtern.",
      messageBody: [
        "In wenigen Minuten können Sie Ihren Beruf oder Ihre Erfahrung, die von Ihnen gesprochenen Sprachen, Ihre Verfügbarkeit, Ihr Mobilitätsprojekt und die für Sie wichtigen Bedingungen genauer beschreiben.",
        "Ob Sie in Luxemburg, in einem Nachbarland oder anderswo in Europa arbeiten möchten: Dieser Dienst hilft dabei, Möglichkeiten zu erkennen, die zu Ihrer Situation passen.",
        "Diese Informationen helfen uns, die Chancen besser zu identifizieren, die für Sie interessant sein könnten."
      ],
      messageHighlight: "Sie antworten nur einmal, und Ihr Profil kann anschließend für verschiedene Chancen berücksichtigt werden.",
      benefitsTitle: "Was Ihnen der Dienst bringen kann",
      benefits: [
        "Mehr Chancen entdecken.",
        "Mit Arbeitgebern in Kontakt kommen.",
        "Zugang zu einem größeren Arbeitsmarkt erhalten.",
        "Ihr Mobilitätsprojekt schrittweise aufbauen."
      ],
      bulletsTitle: "Berufe, die aktuell mit Arbeitgebern in Luxemburg getestet werden",
      bulletsLead: "Die ersten Tests betreffen mehrere rekrutierende Bereiche, insbesondere mit Arbeitgebern in Luxemburg.",
      bullets: [
        "Verkauf und Handel",
        "Reinigung und Instandhaltung",
        "Hotellerie und Gastronomie",
        "Landwirtschaft und Ernte",
        "Vielseitige Tätigkeiten und Jobs mit schnellem Einstieg"
      ],
      sideTitle: "Über EURES",
      sideText: "EURES ist das europäische Kooperationsnetzwerk für Beschäftigung. Es unterstützt berufliche Mobilität und erleichtert Rekrutierungen zwischen europäischen Ländern.",
      disclaimerTitle: "Wie es danach weitergeht",
      disclaimerText: "Ziel ist es, Ihnen berufliche Chancen sichtbar zu machen, die zu Ihrem Profil und Ihrem Mobilitätsprojekt passen.",
      processBullets: [
        "1. Prüfung des Profils.",
        "2. Suche nach passenden Chancen.",
        "3. Vorschläge für Vermittlungen, wenn Bedarfe passen.",
        "4. Schrittweise Erweiterung des Dienstes um mehr Arbeitgeber, Länder und Berufe."
      ],
      tags: ["EURES", "France Travail", "Europäische Union", "Luxemburg", "Verkauf & Handel"],
      logos: {
        eures: {
          src: "https://eures.europa.eu/sites/default/files/site-logo-overrides/EURES%20Gradient%20logo%20SVG%20stretched.svg",
          alt: "EURES-Logo"
        },
        franceTravail: {
          src: "https://cdn.francetravail.fr/studio/logos/marque/favicon/favicon.svg",
          alt: "France-Travail-Logo"
        },
        europeanUnion: {
          src: "https://european-union.europa.eu/themes/contrib/oe_theme/dist/eu/images/logo/condensed-version/positive/logo-eu--en.svg",
          alt: "Logo der Europäischen Union"
        }
      }
    },
    employerLanding: {
      kicker: "Arbeitgeberpfad",
      title: "Einfacher rekrutieren dank europäischer Mobilität",
      lede: "Beschreiben Sie Ihren Rekrutierungsbedarf in wenigen Minuten und lassen Sie uns Kandidatinnen und Kandidaten identifizieren, die zu Ihrer Suche passen könnten, auch über Ihren lokalen Markt hinaus.",
      messageTitle: "Warum diesen Fragebogen ausfüllen?",
      messageIntro: "Dieser Dienst richtet sich an Arbeitgeber, die grenzüberschreitend rekrutieren oder offen für Kandidatinnen und Kandidaten aus anderen europäischen Ländern sind.",
      messageBody: [
        "Der Fragebogen hilft dabei, die Stelle, die gesuchten Kompetenzen, die nützlichen Sprachen, die angebotenen Bedingungen und eventuelle mobilitätsbezogene Bedarfe besser zu verstehen.",
        "Unser Ziel ist es, Ihnen Zugang zu einem größeren Bewerberpool zu geben und Vermittlungen zu erleichtern, wenn Stellen schwer zu besetzen sind.",
        "Je präziser Ihr Bedarf beschrieben ist, desto besser können wir passende Profile identifizieren."
      ],
      messageHighlight: "Dieser Dienst soll Ihnen Zeit sparen und helfen, Ihre Kandidatensuche zu erweitern, wenn Rekrutierung schwieriger wird.",
      benefitsTitle: "Was Ihnen der Dienst bringen kann",
      benefits: [
        "Zugang zu einem größeren Kandidatenpool.",
        "Zeit sparen.",
        "Die Qualität der Vermittlungen verbessern.",
        "Unterstützung bei einem europäischen Rekrutierungsansatz erhalten."
      ],
      bulletsTitle: "Besonders betroffene Bereiche",
      bulletsLead: "Der Dienst ist besonders nützlich, wenn Rekrutierungen schwierig sind oder wenn Bedarfe saisonal oder wiederkehrend sind.",
      bullets: [
        "Verkauf und Handel",
        "Reinigung und Instandhaltung",
        "Hotellerie und Gastronomie",
        "Landwirtschaft und Ernte",
        "Vielseitige Tätigkeiten und Jobs mit schnellem Einstieg"
      ],
      sideTitle: "Ein einfacher und nützlicher Dienst",
      sideText: "Sie beschreiben Ihren Bedarf einmal. Auf dieser Grundlage suchen wir anschließend nach Profilen, die passen könnten, und erleichtern bei Bedarf den Austausch.",
      disclaimerTitle: "Wie es danach weitergeht",
      disclaimerText: "Ziel ist nicht, Ihnen ein zusätzliches Formular aufzuerlegen, sondern Ihnen zu helfen, die benötigten Kandidatinnen und Kandidaten leichter zu finden.",
      processBullets: [
        "1. Prüfung des Bedarfs.",
        "2. Suche nach passenden Profilen.",
        "3. Vorschläge für Vermittlungen, wenn Kandidatinnen und Kandidaten passen.",
        "4. Schrittweise Verbesserung des Dienstes."
      ],
      tags: ["EURES", "France Travail", "Europäische Union", "Luxemburg", "Rekrutierung"]
    },
    candidateQuestionnaire: {
      eyebrow: "Kandidatenfragebogen",
      title: "Erstes Matching-Signal für Kandidaten",
      lede: "Wir erfassen hier die minimal nötigen Informationen für spätere passende Vorschläge.",
      sections: {
        mobility: "Mobilitätsprojekt",
        profile: "Berufliches Profil",
        contact: "Kontaktdaten"
      },
      fields: {
        residenceCountry: "Wohnland",
        targetCountries: "Zielländer",
        mobilityType: "Mobilitätsart",
        availability: "Verfügbarkeit",
        sectors: "Zielbranchen",
        experienceLevel: "Erfahrungsniveau",
        languages: "Arbeitssprachen",
        fullName: "Vollständiger Name",
        email: "E-Mail",
        phone: "Telefon",
        city: "Aktueller Wohnort",
        notes: "Zusätzliche Hinweise"
      },
      options: {
        targetCountries: ["Luxemburg", "Frankreich", "Deutschland", "Belgien"],
        mobilityType: ["Grenzüberschreitend", "Umzug", "Beides"],
        availability: ["Sofort", "Innerhalb 1 Monats", "Innerhalb 3 Monaten", "Später"],
        sectors: ["Verkauf und Handel", "Reinigung und Instandhaltung", "Hotellerie und Gastronomie", "Landwirtschaft und Ernte", "Flexible Einstiegsjobs"],
        experienceLevel: ["Mehr als 2 Jahre", "6 Monate bis 2 Jahre", "Weniger als 6 Monate", "Anfänger, aber motiviert"],
        languages: ["Französisch", "Englisch", "Deutsch", "Luxemburgisch"]
      },
      helper: "Später kann der Ablauf um CV-Upload, Verwaltungsdokumente und branchenspezifische Details erweitert werden."
    },
    employerQuestionnaire: {
      eyebrow: "Arbeitgeberfragebogen",
      title: "Erstes Matching-Signal für Arbeitgeber",
      lede: "Wir erfassen hier die minimal nötigen Informationen, um kompatible Profile vorzuschlagen.",
      sections: {
        need: "Personalbedarf",
        conditions: "Rahmenbedingungen",
        contact: "Kontaktdaten"
      },
      fields: {
        companyName: "Unternehmensname",
        workLocation: "Arbeitsort",
        sector: "Hauptbranche",
        recruitCount: "Anzahl Einstellungen",
        startDate: "Startdatum oder Zeitraum",
        languagesRequired: "Erforderliche Sprachen",
        contractDuration: "Vertragsdauer",
        weeklyHours: "Wochenstunden",
        installationSupport: "Unterstützung bei Ankunft",
        criticalCriteria: "Wichtige Kriterien",
        contactName: "Kontaktperson",
        email: "E-Mail",
        phone: "Telefon",
        notes: "Details zur Stelle"
      },
      options: {
        sector: ["Verkauf und Handel", "Reinigung und Instandhaltung", "Hotellerie und Gastronomie", "Landwirtschaft und Ernte", "Flexible Einstiegsjobs"],
        recruitCount: ["1", "2 bis 5", "6 bis 10", "10+"],
        languagesRequired: ["Französisch", "Englisch", "Deutsch", "Luxemburgisch"],
        contractDuration: ["Saisonal", "Befristet", "Unbefristet", "Noch offen"],
        weeklyHours: ["Vollzeit", "Teilzeit", "Variabel"],
        installationSupport: ["Keine Unterstützung", "Administrative Hilfe", "Wohnungshilfe", "Transporthilfe"],
        criticalCriteria: ["Schnelle Verfügbarkeit", "Branchenerfahrung", "Gesprochene Sprache", "Selbstständigkeit", "Mobilität"]
      },
      helper: "Später kann das Scoring um feinere Kriterien je Branche und menschliche Validierung ergänzt werden."
    },
    statPage: {
      eyebrow: "Öffentliches Beobachtungsportal des Experiments",
      title: "Verfolgung des EURES-beta-Experiments",
      lede: "Diese Seite zeigt die wichtigsten Indikatoren zur Beobachtung des EURES-beta-Experiments.\n\nDie veröffentlichten Daten sind aggregiert und anonymisiert. Sie machen die Aktivität des Projekts und erste Erkenntnisse aus der Nutzung sichtbar.",
      updatedPrefix: "Letzte Aktualisierung",
      methodologyTitle: "Methodik",
      methodology: "Die veröffentlichten Daten sind aggregiert und anonymisiert. Sie dienen der Beobachtung des Experiments, ohne personenbezogene Daten anzuzeigen.",
      manualNote: "Indikatoren zur Funktionsbeobachtung zeigen Vermittlungen, Rückmeldungen und die wichtigsten Schritte im Ablauf.",
      manualMissing: "Die Indikatoren zur Funktionsbeobachtung werden mit dem Ausbau des Experiments schrittweise ergänzt.",
      keyFiguresTitle: "Kennzahlen",
      keyFiguresLead: "Diese ersten Ergebnisse zeigen die Dynamik des Experiments und erste Verbindungen zwischen Personalbedarf und Mobilitätsplänen.",
      observationsTitle: "Was wir beobachten",
      observationsLead: "Die ersten Nutzungen zeigen bereits vertretene Branchen, Mobilitätsmuster und beteiligte Gebiete.",
      observationsCards: {
        sectors: "Derzeit vertretene Branchen",
        mobility: "Gesuchte Mobilität",
        territories: "Beteiligte Gebiete"
      },
      observationsTexts: {
        sectors: "Die ersten vertretenen Branchen entsprechen den Berufen, die im Rahmen des Experiments derzeit untersucht werden.",
        mobility: "Die ersten Kandidatinnen und Kandidaten richten ihren Blick vor allem auf Luxemburg, auf grenzüberschreitende Wege oder andere europäische Ziele.",
        territories: "Die ersten erfassten Bedarfe und Vorhaben zeigen bereits eine aktive Dynamik zwischen mehreren Ländern der Großregion und darüber hinaus."
      },
      learningsTitle: "Erste Erkenntnisse",
      learnings: [
        ["Es gibt Nachfrage", "Die ersten Ergebnisse zeigen sowohl Personalbedarf als auch Interesse von Kandidatinnen und Kandidaten, die berufliche Mobilität in Betracht ziehen."],
        ["Annäherungen sind möglich", "Das Experiment hilft, Kompatibilitäten zwischen Arbeitgeberbedarfen und Kandidatenvorhaben zu erkennen."],
        ["Schrittweiser Ausbau", "Der Ansatz soll schrittweise mit mehr Arbeitgebern, Branchen und Gebieten wachsen."]
      ],
      detailedTitle: "Detaillierte Daten",
      detailedLead: "Die folgenden Bereiche ermöglichen eine vertiefte Lektüre der im Experiment beobachteten Nutzungsmuster.",
      monthlyTitle: "Monatliche Entwicklung",
      monthlyLead: "Die monatliche Entwicklung zeigt den Ausbau des Angebots, die Intensität der Nutzung und erste beobachtete Ergebnisse.",
      breakdownsTitle: "Detaillierte Verteilungen",
      durationsTitle: "Indikatoren zur Funktionsbeobachtung",
      hoursUnit: "Std.",
      daysUnit: "Tg.",
      noDurationData: "k. A.",
      totals: {
        candidats: "Kandidaten-Eingänge",
        besoins_employeurs: "Arbeitgeberbedarfe",
        matchings: "Berechnete Matchings",
        candidats_contactes: "Kontaktierte Kandidaten",
        candidatures_transmises_employeur: "Übermittelte Bewerbungen",
        contacts_acceptes_employeur: "Vom Arbeitgeber akzeptierte Kontakte",
        contacts_refuses_employeur: "Vom Arbeitgeber abgelehnte Kontakte",
        contacts_sans_reponse_employeur: "Kontakte ohne Arbeitgeberantwort",
        embauches: "Einstellungen"
      },
      monthlyColumns: {
        mois: "Monat",
        candidats: "Kandidaten",
        besoins_employeurs: "Arbeitgeberbedarfe",
        matchings: "Matchings",
        candidats_contactes: "Kontaktierte Kandidaten",
        candidatures_transmises_employeur: "Übermittelte Bewerbungen",
        contacts_acceptes_employeur: "Akzeptiert",
        contacts_refuses_employeur: "Abgelehnt",
        contacts_sans_reponse_employeur: "Ohne Antwort",
        embauches: "Einstellungen"
      },
      breakdownLabels: {
        besoins_par_pays: "Arbeitgeberbedarfe nach Land",
        secteurs: "Sektoren",
        mobilite_candidats: "Mobilität der Kandidaten",
        experience_internationale_candidats: "Internationale Erfahrung der Kandidaten",
        matchings_par_statut: "Matching-Status",
        retours_employeurs: "Arbeitgeber-Rückmeldungen"
      },
      durationLabels: {
        calcul_to_admin: "Berechnung → Admin-Entscheidung",
        admin_to_send: "Admin-Entscheidung → Versand Arbeitgeber",
        send_to_employer_response: "Versand Arbeitgeber → Antwort Arbeitgeber",
        response_to_relation: "Arbeitgeberantwort → Kontaktaufnahme",
        relation_to_hire: "Kontaktaufnahme → Einstellung"
      },
      durationMetrics: {
        count: "Gemessene Fälle",
        avg: "Durchschnitt",
        median: "Median",
        min: "Minimum",
        max: "Maximum"
      },
      emptyBreakdown: "Noch keine auswertbaren Daten.",
      loading: "Statistiken werden geladen...",
      error: "Die Statistiken können derzeit nicht geladen werden."
    }
  }
};

const candidateTallyMeta = {
  formId: "449blX",
  mobilityTypes: ["Transfrontalière", "Expatriation"],
  countryColumns: ["J'y habite", "Je veux y travailler", "J'y ai déjà travaillé"],
  countryRows: [
    { field: "tally_q01_f01", label: "Allemagne" },
    { field: "tally_q01_f02", label: "France" },
    { field: "tally_q01_f03", label: "Luxembourg" },
    { field: "tally_q01_f04", label: "Un autre pays de l'UE" },
    { field: "tally_q01_f05", label: "Un autre pays hors UE" }
  ],
  scheduleColumns: ["Matin", "Après-midi", "Soir", "Nuit"],
  scheduleRows: [
    { field: "tally_q07_f01", label: "Lundi" },
    { field: "tally_q07_f02", label: "Mardi" },
    { field: "tally_q07_f03", label: "Mercredi" },
    { field: "tally_q07_f04", label: "Jeudi" },
    { field: "tally_q07_f05", label: "Vendredi" },
    { field: "tally_q07_f06", label: "Samedi" },
    { field: "tally_q07_f07", label: "Dimanche" }
  ],
  documentsColumns: ["Je l'ai", "Je suis en train de le préparer", "Je ne sais pas encore"],
  documentsRows: [
    { field: "tally_q10_f01", label: "Carte d'identité ou passeport (en cours de validité)" },
    { field: "tally_q10_f02", label: "CV à jour" },
    { field: "tally_q10_f03", label: "Vos diplômes ou qualifications professionnelles" },
    { field: "tally_q10_f04", label: "Compte bancaire / IBAN" },
    { field: "tally_q10_f05", label: "Attestation d'affiliation à la sécurité sociale" }
  ],
  languageColumns: [
    "Langue maternelle",
    "Je peux échanger à l'oral",
    "Je peux travailler avec cette langue",
    "J'utilise un outil de traduction si nécessaire",
    "Je ne la pratique pas"
  ],
  languageRows: [
    { field: "tally_q18_f01", label: "Allemand" },
    { field: "tally_q18_f02", label: "Anglais" },
    { field: "tally_q18_f03", label: "Français" },
    { field: "tally_q18_f04", label: "Luxembourgeois" }
  ],
  rankingOptions: [
    "Trouver un logement",
    "Trouver un emploi",
    "Comprendre les démarches administratives/fiscales",
    "Préparer votre budget et vos finances",
    "Améliorer votre niveau de langue",
    "Obtenir de l'aide à l'arrivée (installation, démarches)",
    "Construire un réseau, vous intégrer socialement"
  ],
  sectors: [
    "Vente et commerce (ex : prêt-à-porter, chaussures, commerce spécialisé)",
    "Nettoyage et entretien (ex : bureaux, espaces collectifs)",
    "Hôtellerie et restauration (ex : plonge, service, aide de cuisine)",
    "Agriculture et récolte (ex : récolte de fruits, travaux saisonniers)",
    "Missions polyvalentes et emplois accessibles rapidement"
  ]
};

const candidateTallyCopy = {
  fr: {
    eyebrow: "Questionnaire candidat EURES",
    heroTitle: "Mobilité européenne, transfrontalière ou expatriation",
    heroLede: "Ce questionnaire nous aide à mieux comprendre votre projet de mobilité en Europe, que vous envisagiez de travailler dans un pays voisin ou de partir vivre et travailler dans un autre pays européen.",
    heroHighlight: "Quelques minutes suffisent. Vos réponses nous permettent de voir plus rapidement si des opportunités peuvent correspondre à votre situation, à vos disponibilités et à vos préférences.",
    matrixMobileHint: "Sur téléphone et tablette, chaque ligne s'affiche verticalement pour faciliter la lecture.",
    overviewTitle: "Concernant votre projet de mobilité",
    overviewMatrixTitle: "Sélectionner ci-dessous votre pays de résidence, le(s) pays où vous souhaitez travailler et ceux où vous avez déjà travaillé",
    mobilityTypeTitle: "Quel type de mobilité envisagez vous ?",
    mobilityTypeHint: "Vous pouvez choisir une seule option ou les deux.",
    crossBorderTitle: "Votre projet de mobilité transfrontalière",
    expatriationTitle: "Votre projet d'expatriation",
    professionalTitle: "Votre projet professionnel",
    contactTitle: "Pour pouvoir vous recontacter",
    rankingTitle: "Classez du plus important au moins important pour vous ces propositions ?",
    rankingHint: "Attribuez un rang unique à chaque proposition : 1 pour le plus important, 7 pour le moins important.",
    sidebarWhyTitle: "Pourquoi ce questionnaire ?",
    sidebarWhyText: "Il sert à repérer plus facilement les personnes qui peuvent être intéressées par une opportunité de mobilité européenne, en fonction du pays visé, du métier, des langues, de la disponibilité et des conditions pratiques.",
    sidebarAfterTitle: "Et après ?",
    sidebarAfterText: "Si votre profil semble correspondre à un besoin en cours, il pourra être étudié pour une mise en relation. Si ce n’est pas encore le bon moment, vos réponses nous aident aussi à mieux préparer les prochaines opportunités.",
    sidebarResumeTitle: "Reprendre plus tard",
    sidebarResumeText: "Un identifiant est conservé pour retrouver votre progression si besoin.",
    salaryExpectationIntro: "Indiquez ici votre attente salariale pour ce métier, en euros, en précisant s'il s'agit d'un montant brut ou net.",
    fileNote: "Le nom du fichier sera enregistré. Le fichier lui-même n’est pas encore stocké côté plateforme.",
    consentText: "J’accepte que mes réponses soient utilisées par les équipes et partenaires EURES dans le cadre de l’accompagnement à la mobilité professionnelle et des mises en relation proposées. Vos données seront utilisées uniquement dans le cadre de votre accompagnement et conformément à la réglementation européenne sur la protection des données (RGPD).",
    rankingError: "Chaque priorité d'expatriation doit avoir un rang unique de 1 à 7.",
    errors: {
      maxFour: "Vous avez déjà choisi 4 éléments pour cette section."
    },
    mobilityTypeOptions: ["Transfrontalière", "Expatriation"],
    countryColumns: ["J'y habite", "Je veux y travailler", "J'y ai déjà travaillé"],
    countryRows: ["Allemagne", "France", "Luxembourg", "Un autre pays de l'UE", "Un autre pays hors UE"],
    scheduleColumns: ["Matin", "Après-midi", "Soir", "Nuit"],
    scheduleRows: ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"],
    documentsColumns: ["Je l'ai", "Je suis en train de le préparer", "Je ne sais pas encore"],
    documentsRows: [
      "Carte d'identité ou passeport (en cours de validité)",
      "CV à jour",
      "Vos diplômes ou qualifications professionnelles",
      "Compte bancaire / IBAN",
      "Attestation d'affiliation à la sécurité sociale"
    ],
    languageColumns: [
      "Langue maternelle",
      "Je peux échanger à l'oral",
      "Je peux travailler avec cette langue",
      "J'utilise un outil de traduction si nécessaire",
      "Je ne la pratique pas"
    ],
    languageRows: ["Allemand", "Anglais", "Français", "Luxembourgeois"],
    rankingOptions: [
      "Trouver un logement",
      "Trouver un emploi",
      "Comprendre les démarches administratives/fiscales",
      "Préparer votre budget et vos finances",
      "Améliorer votre niveau de langue",
      "Obtenir de l'aide à l'arrivée (installation, démarches)",
      "Construire un réseau, vous intégrer socialement"
    ],
    sectors: [
      "Vente et commerce (ex : prêt-à-porter, chaussures, commerce spécialisé)",
      "Nettoyage et entretien (ex : bureaux, espaces collectifs)",
      "Hôtellerie et restauration (ex : plonge, service, aide de cuisine)",
      "Agriculture et récolte (ex : récolte de fruits, travaux saisonniers)",
      "Missions polyvalentes et emplois accessibles rapidement"
    ],
    questions: {
      q03: "Avez-vous déjà travaillé sous statut \"frontalier\" ?",
      q04: "Quel temps de trajet maximum accepteriez vous de faire (aller simple) ?",
      q05: "Comment vous vous déplaceriez au quotidien ?",
      q06: "Quelles sont vos disponibilités horaires ?",
      q07: "Sélectionner vos disponibilités",
      q08: "Quels types de contrats accepteriez vous ?",
      q09: "À partir de quand seriez-vous disponible pour commencer un emploi ?",
      q10: "Où en êtes-vous dans la préparation de ces documents ?",
      q10Hint: "Il n’est pas nécessaire d’avoir déjà tous les documents.",
      q11: "Avez-vous déjà un numéro ou une affiliation à la sécurité sociale luxembourgeoise ?",
      q12: "Avez-vous déjà un numéro ou une affiliation à la sécurité sociale allemande ?",
      q13: "Avez-vous déjà un numéro ou une affiliation à la sécurité sociale française ?",
      q14: "Avez-vous déjà vécu et travaillé dans pays étranger ?",
      q15: "Quand souhaitez-vous partir ?",
      q16: "Concernant les conditions de votre départ, vous partirez :",
      q18: "Vos compétences linguistiques",
      q19: "Dans quels secteurs souhaitez-vous travailler ?",
      sectorHint: "Vous pouvez sélectionner jusqu'à 4 propositions.",
      q21: "Avez-vous une expérience professionnelle dans le secteur de la vente et du commerce ?",
      q23: "Avez-vous une expérience professionnelle dans le secteur du nettoyage ?",
      q24: "Disposez-vous d’un extrait de casier judiciaire (bulletin n°3) datant de moins de 3 mois ?",
      q26: "Avez-vous une expérience professionnelle dans le secteur de l'hôtellerie et de la restauration?",
      q28: "Avez-vous une expérience professionnelle dans le secteur de l'agriculture et de la récolte?",
      q30: "Avez-vous une expérience professionnelle ?",
      salaryType: "Sous quelle forme pensez-vous à votre salaire ?",
      salaryMin: "Quel est le minimum que vous souhaiteriez pour ce métier, en euros bruts ou nets ?",
      firstName: "Prénom",
      lastName: "Nom",
      email: "Adresse e-mail",
      phone: "Téléphone",
      city: "Ville de résidence actuelle",
      cv: "Souhaitez-vous transmettre votre CV ?"
    },
    options: {
      yesNo: ["Oui", "Non"],
      yesNoUnknown: ["Oui", "Non", "Je ne sais pas"],
      commute: ["30 min", "1h", "1h30", "2h", "Plus de 2h"],
      transport: ["Voiture", "Train", "Bus", "Covoiturage", "Je ne sais pas encore"],
      schedule: ["Je suis disponible sur des horaires variés", "J’ai des contraintes ou préférences horaires"],
      contracts: ["CDI", "CDD", "Intérim", "Saisonnier", "Temps plein", "Temps partiel"],
      startDate: ["Dès que possible", "Dans les prochains jours", "Dans les prochaines semaines", "Dans 1 à 3 mois", "Je ne sais pas encore"],
      departWhen: ["Dès que possible", "D'ici 3 mois", "Entre 3 et 6 mois", "Dans  plus de 6 mois", "Je ne sais pas"],
      departWith: ["Uniquement vous", "En couple", "En famille"],
      experience: ["Oui, plus de 2 ans", "Oui, entre 6 mois et 2 ans", "Oui, moins de 6 mois", "Non, mais je suis intéressé(e) par le secteur"],
      backgroundCheck: ["Oui", "Non", "Je peux en faire la demande rapidement", "Je ne sais pas"]
    },
    salaryUnits: ["Par heure", "Par mois", "Par an"],
    salaryFields: {
      type: "Sous quelle forme pensez-vous à votre salaire ?",
      min: "Quel est le minimum que vous souhaiteriez pour ce métier, en euros bruts ou nets ?"
    },
    sectorTitles: {
      vente: "Vente et commerce",
      nettoyage: "Nettoyage et entretien",
      hotel: "Hôtellerie et restauration",
      agri: "Agriculture et récolte",
      polyvalent: "Missions polyvalentes et emplois accessibles rapidement"
    },
    sectorLegends: {
      vente: "Vente et commerce — parmi les propositions suivantes, lesquelles vous correspondent le mieux ?",
      nettoyage: "Nettoyage et entretien — parmi les propositions suivantes, lesquelles vous correspondent le mieux ?",
      hotel: "Hôtellerie et restauration — parmi les propositions suivantes, lesquelles vous correspondent le mieux ?",
      agri: "Agriculture et récolte — parmi les propositions suivantes, lesquelles vous correspondent le mieux ?",
      polyvalent: "Missions polyvalentes et emplois accessibles rapidement — parmi les propositions suivantes, lesquelles vous correspondent le mieux ?"
    },
    sectorChoices: {
      vente: [
        "Accueillir et orienter les clients",
        "Conseiller un produit ou un service",
        "Comprendre rapidement une demande",
        "Réaliser un encaissement",
        "Garder son calme en période d’affluence",
        "Travailler en équipe",
        "Être ponctuel",
        "S’adapter à différentes tâches",
        "Résister au stress",
        "Aider un collègue si nécessaire",
        "Fidéliser la clientèle",
        "Maintenir un espace de vente propre et organisé"
      ],
      nettoyage: [
        "Travailler de manière autonome",
        "Appliquer des consignes",
        "Organiser son travail",
        "Maintenir un espace propre et organisé",
        "S'adapter à une situation imprévue",
        "Prendre soin du matériel utilisé",
        "Être efficace dans ses tâches",
        "Travailler en équipe",
        "Aider un collègue si nécessaire",
        "Être ponctuel",
        "Respecter des règles d’hygiène et de sécurité",
        "Effectuer des tâches répétitives"
      ],
      hotel: [
        "Accueillir et orienter les clients",
        "Travailler en équipe",
        "Garder son calme pendant les périodes d’affluence",
        "Appliquer des consignes",
        "Être ponctuel",
        "S’adapter à différentes tâches",
        "Mémoriser des commandes ou des informations",
        "Aider un collègue si nécessaire",
        "Résister au stress",
        "Maintenir un espace propre et organisé",
        "Conseiller un client ou répondre à une demande"
      ],
      agri: [
        "Être ponctuel",
        "Travailler en équipe",
        "Appliquer des consignes",
        "Prendre soin du matériel utilisé",
        "Aider un collègue si nécessaire",
        "Garder son calme en période d’activité intense",
        "Réaliser des tâches physiques",
        "Travailler en extérieur et selon les conditions météo",
        "S’adapter à différentes tâches",
        "Effectuer des tâches répétitives"
      ],
      polyvalent: [
        "S’adapter rapidement à une nouvelle tâche",
        "Travailler en équipe",
        "Respecter les consignes",
        "Respecter les horaires de travail",
        "Réaliser un travail physique",
        "Travailler à un rythme soutenu",
        "Travailler dans différents environnements",
        "Accepter des horaires variables",
        "Aider un collègue si nécessaire",
        "Être disponible rapidement"
      ]
    }
  },
  en: {
    eyebrow: "EURES candidate questionnaire",
    heroTitle: "European mobility, cross-border commuting or relocation",
    heroLede: "This questionnaire helps us better understand your mobility plans in Europe, whether you are considering working in a neighbouring country or moving to live and work in another European country.",
    heroHighlight: "It only takes a few minutes. Your answers help us identify more quickly whether opportunities may match your situation, availability and preferences.",
    matrixMobileHint: "On mobile and tablet, each row is displayed vertically for easier reading.",
    overviewTitle: "About your mobility plans",
    overviewMatrixTitle: "Select below your country of residence, the country or countries where you would like to work, and those where you have already worked",
    mobilityTypeTitle: "What type of mobility are you considering?",
    mobilityTypeHint: "You can choose one option or both.",
    crossBorderTitle: "Your cross-border mobility plans",
    expatriationTitle: "Your relocation plans",
    professionalTitle: "Your professional plans",
    contactTitle: "So that we can contact you again",
    rankingTitle: "Rank these items from most important to least important for you",
    rankingHint: "Give a unique rank to each item: 1 for the most important, 7 for the least important.",
    sidebarWhyTitle: "Why this questionnaire?",
    sidebarWhyText: "It helps us identify more easily people who may be interested in a European mobility opportunity, based on the target country, job sector, languages, availability and practical conditions.",
    sidebarAfterTitle: "What happens next?",
    sidebarAfterText: "If your profile seems to match an active need, it may be reviewed for a possible introduction. If the timing is not right yet, your answers still help us prepare upcoming opportunities better.",
    sidebarResumeTitle: "Continue later",
    sidebarResumeText: "An identifier is kept so your progress can be found again if needed.",
    salaryExpectationIntro: "Indicate your salary expectation for this role here, in euros, and specify whether it is gross or net.",
    fileNote: "The file name will be recorded. The file itself is not yet stored on the platform.",
    consentText: "I agree that my answers may be used by EURES teams and partners for professional mobility support and the proposed introductions. Your data will only be used for your support and in accordance with European data protection rules (GDPR).",
    rankingError: "Each relocation priority must have a unique rank from 1 to 7.",
    errors: {
      maxFour: "You have already selected 4 items for this section."
    },
    mobilityTypeOptions: ["Cross-border commuting", "Relocation"],
    countryColumns: ["I live there", "I want to work there", "I have already worked there"],
    countryRows: ["Germany", "France", "Luxembourg", "Another EU country", "Another non-EU country"],
    scheduleColumns: ["Morning", "Afternoon", "Evening", "Night"],
    scheduleRows: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    documentsColumns: ["I already have it", "I am preparing it", "I do not know yet"],
    documentsRows: [
      "Identity card or passport (valid)",
      "Up-to-date CV",
      "Your diplomas or professional qualifications",
      "Bank account / IBAN",
      "Social security affiliation certificate"
    ],
    languageColumns: [
      "Native language",
      "I can speak it",
      "I can work in this language",
      "I use a translation tool if needed",
      "I do not use it"
    ],
    languageRows: ["German", "English", "French", "Luxembourgish"],
    rankingOptions: [
      "Finding accommodation",
      "Finding a job",
      "Understanding administrative and tax procedures",
      "Planning your budget and finances",
      "Improving your language level",
      "Getting help on arrival (settling in, procedures)",
      "Building a network and integrating socially"
    ],
    sectors: [
      "Sales and retail (for example ready-to-wear, shoes, specialist retail)",
      "Cleaning and maintenance (for example offices, shared spaces)",
      "Hospitality and food service (for example dishwashing, service, kitchen support)",
      "Agriculture and harvesting (for example fruit picking, seasonal work)",
      "Versatile jobs and roles accessible quickly"
    ],
    questions: {
      q03: "Have you already worked with cross-border commuter status?",
      q04: "What maximum travel time would you accept (one way)?",
      q05: "How would you travel on a daily basis?",
      q06: "What are your schedule availabilities?",
      q07: "Select your availabilities",
      q08: "Which types of contract would you accept?",
      q09: "When would you be available to start a job?",
      q10: "Where do you stand in preparing these documents?",
      q10Hint: "It is not necessary to already have all of them.",
      q11: "Do you already have a Luxembourg social security number or affiliation?",
      q12: "Do you already have a German social security number or affiliation?",
      q13: "Do you already have a French social security number or affiliation?",
      q14: "Have you already lived and worked in a foreign country?",
      q15: "When would you like to leave?",
      q16: "Regarding your departure, you would leave:",
      q18: "Your language skills",
      q19: "In which sectors would you like to work?",
      sectorHint: "You can select up to 4 options.",
      q21: "Do you have work experience in sales and retail?",
      q23: "Do you have work experience in cleaning?",
      q24: "Do you have a criminal record extract issued within the last 3 months?",
      q26: "Do you have work experience in hospitality and food service?",
      q28: "Do you have work experience in agriculture and harvesting?",
      q30: "Do you have work experience?",
      salaryType: "How do you think about your salary?",
      salaryMin: "What is the minimum you would like for this role, in gross or net euros?",
      firstName: "First name",
      lastName: "Last name",
      email: "Email address",
      phone: "Phone",
      city: "Current city of residence",
      cv: "Would you like to provide your CV?"
    },
    options: {
      yesNo: ["Yes", "No"],
      yesNoUnknown: ["Yes", "No", "I don't know"],
      commute: ["30 min", "1h", "1h30", "2h", "More than 2h"],
      transport: ["Car", "Train", "Bus", "Carpooling", "I don't know yet"],
      schedule: ["I am available on varied schedules", "I have schedule constraints or preferences"],
      contracts: ["Permanent contract", "Fixed-term contract", "Temporary agency work", "Seasonal", "Full-time", "Part-time"],
      startDate: ["As soon as possible", "In the next few days", "In the next few weeks", "In 1 to 3 months", "I don't know yet"],
      departWhen: ["As soon as possible", "Within 3 months", "Between 3 and 6 months", "In more than 6 months", "I don't know"],
      departWith: ["Only you", "As a couple", "As a family"],
      experience: ["Yes, more than 2 years", "Yes, between 6 months and 2 years", "Yes, less than 6 months", "No, but I am interested in this sector"],
      backgroundCheck: ["Yes", "No", "I can request it quickly", "I don't know"]
    },
    salaryUnits: ["Per hour", "Per month", "Per year"],
    salaryFields: {
      type: "How do you think about your salary?",
      min: "What is the minimum you would like for this role, in gross or net euros?"
    },
    sectorTitles: {
      vente: "Sales and retail",
      nettoyage: "Cleaning and maintenance",
      hotel: "Hospitality and food service",
      agri: "Agriculture and harvesting",
      polyvalent: "Versatile jobs and roles accessible quickly"
    },
    sectorLegends: {
      vente: "Sales and retail: which of the following statements describe you best?",
      nettoyage: "Cleaning and maintenance: which of the following statements describe you best?",
      hotel: "Hospitality and food service: which of the following statements describe you best?",
      agri: "Agriculture and harvesting: which of the following statements describe you best?",
      polyvalent: "Versatile jobs and roles accessible quickly: which of the following statements describe you best?"
    },
    sectorChoices: {
      vente: ["Welcoming and guiding customers", "Advising on a product or service", "Understanding a request quickly", "Handling payment", "Staying calm during busy periods", "Working as part of a team", "Being punctual", "Adapting to different tasks", "Handling stress", "Helping a colleague when needed", "Building customer loyalty", "Keeping the sales area clean and organised"],
      nettoyage: ["Working independently", "Following instructions", "Organising your work", "Keeping an area clean and organised", "Adapting to an unexpected situation", "Taking care of the equipment used", "Being efficient in your tasks", "Working as part of a team", "Helping a colleague when needed", "Being punctual", "Following hygiene and safety rules", "Carrying out repetitive tasks"],
      hotel: ["Welcoming and guiding customers", "Working as part of a team", "Staying calm during busy periods", "Following instructions", "Being punctual", "Adapting to different tasks", "Remembering orders or information", "Helping a colleague when needed", "Handling stress", "Keeping an area clean and organised", "Advising a customer or answering a request"],
      agri: ["Being punctual", "Working as part of a team", "Following instructions", "Taking care of the equipment used", "Helping a colleague when needed", "Staying calm during intense periods of activity", "Doing physical tasks", "Working outdoors and depending on weather conditions", "Adapting to different tasks", "Carrying out repetitive tasks"],
      polyvalent: ["Adapting quickly to a new task", "Working as part of a team", "Following instructions", "Respecting working hours", "Doing physical work", "Working at a sustained pace", "Working in different environments", "Accepting variable schedules", "Helping a colleague when needed", "Being available quickly"]
    }
  },
  de: {
    eyebrow: "EURES-Kandidatenfragebogen",
    heroTitle: "Europäische Mobilität, Grenzpendeln oder Umzug",
    heroLede: "Dieser Fragebogen hilft uns, Ihre Mobilitätspläne in Europa besser zu verstehen, egal ob Sie in einem Nachbarland arbeiten möchten oder in ein anderes europäisches Land ziehen wollen, um dort zu leben und zu arbeiten.",
    heroHighlight: "Das dauert nur wenige Minuten. Ihre Antworten helfen uns, schneller zu erkennen, ob Chancen zu Ihrer Situation, Ihrer Verfügbarkeit und Ihren Präferenzen passen könnten.",
    matrixMobileHint: "Auf Smartphone und Tablet wird jede Zeile untereinander angezeigt, damit sie leichter lesbar ist.",
    overviewTitle: "Zu Ihrem Mobilitätsprojekt",
    overviewMatrixTitle: "Wählen Sie unten Ihr Wohnland, die Länder, in denen Sie arbeiten möchten, und die Länder, in denen Sie bereits gearbeitet haben",
    mobilityTypeTitle: "Welche Art von Mobilität ziehen Sie in Betracht?",
    mobilityTypeHint: "Sie können eine oder beide Optionen wählen.",
    crossBorderTitle: "Ihr grenzüberschreitendes Mobilitätsprojekt",
    expatriationTitle: "Ihr Umzugsprojekt",
    professionalTitle: "Ihr berufliches Projekt",
    contactTitle: "Damit wir Sie wieder kontaktieren können",
    rankingTitle: "Ordnen Sie diese Punkte von am wichtigsten bis am wenigsten wichtig für Sie",
    rankingHint: "Geben Sie jedem Punkt einen eindeutigen Rang: 1 für am wichtigsten, 7 für am wenigsten wichtig.",
    sidebarWhyTitle: "Warum dieser Fragebogen?",
    sidebarWhyText: "Er hilft uns, leichter Personen zu erkennen, die an einer europäischen Mobilitätschance interessiert sein könnten, je nach Zielland, Berufsfeld, Sprachen, Verfügbarkeit und praktischen Bedingungen.",
    sidebarAfterTitle: "Wie geht es danach weiter?",
    sidebarAfterText: "Wenn Ihr Profil zu einem aktuellen Bedarf zu passen scheint, kann es für eine mögliche Vermittlung geprüft werden. Wenn der Zeitpunkt noch nicht passt, helfen uns Ihre Antworten trotzdem dabei, kommende Chancen besser vorzubereiten.",
    sidebarResumeTitle: "Später fortsetzen",
    sidebarResumeText: "Eine Kennung wird gespeichert, damit Ihr Fortschritt bei Bedarf wiedergefunden werden kann.",
    salaryExpectationIntro: "Geben Sie hier Ihre Gehaltserwartung für diesen Beruf in Euro an und präzisieren Sie, ob es sich um einen Brutto- oder Nettobetrag handelt.",
    fileNote: "Der Dateiname wird gespeichert. Die Datei selbst wird derzeit noch nicht auf der Plattform gespeichert.",
    consentText: "Ich stimme zu, dass meine Antworten von EURES-Teams und Partnern für die Begleitung der beruflichen Mobilität und die vorgeschlagenen Vermittlungen verwendet werden dürfen. Ihre Daten werden nur im Rahmen Ihrer Begleitung und gemäß den europäischen Datenschutzvorschriften (DSGVO) verwendet.",
    rankingError: "Jede Umzugspriorität muss einen eindeutigen Rang von 1 bis 7 haben.",
    errors: {
      maxFour: "Sie haben für diesen Abschnitt bereits 4 Elemente ausgewählt."
    },
    mobilityTypeOptions: ["Grenzpendeln", "Umzug"],
    countryColumns: ["Ich wohne dort", "Ich möchte dort arbeiten", "Ich habe dort bereits gearbeitet"],
    countryRows: ["Deutschland", "Frankreich", "Luxemburg", "Ein anderes EU-Land", "Ein anderes Nicht-EU-Land"],
    scheduleColumns: ["Morgen", "Nachmittag", "Abend", "Nacht"],
    scheduleRows: ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"],
    documentsColumns: ["Ich habe es bereits", "Ich bereite es gerade vor", "Ich weiß es noch nicht"],
    documentsRows: [
      "Personalausweis oder Reisepass (gültig)",
      "Aktueller Lebenslauf",
      "Ihre Diplome oder beruflichen Qualifikationen",
      "Bankkonto / IBAN",
      "Bescheinigung über die Sozialversicherungszugehörigkeit"
    ],
    languageColumns: [
      "Muttersprache",
      "Ich kann mich mündlich verständigen",
      "Ich kann in dieser Sprache arbeiten",
      "Ich nutze bei Bedarf ein Übersetzungstool",
      "Ich nutze sie nicht"
    ],
    languageRows: ["Deutsch", "Englisch", "Französisch", "Luxemburgisch"],
    rankingOptions: [
      "Eine Unterkunft finden",
      "Eine Arbeit finden",
      "Verwaltungs- und Steuerverfahren verstehen",
      "Ihr Budget und Ihre Finanzen planen",
      "Ihr Sprachniveau verbessern",
      "Hilfe bei der Ankunft erhalten (Einrichtung, Verfahren)",
      "Ein Netzwerk aufbauen und sich sozial integrieren"
    ],
    sectors: [
      "Verkauf und Handel (z. B. Bekleidung, Schuhe, Fachhandel)",
      "Reinigung und Instandhaltung (z. B. Büros, Gemeinschaftsflächen)",
      "Hotellerie und Gastronomie (z. B. Spülküche, Service, Küchenhilfe)",
      "Landwirtschaft und Ernte (z. B. Obsternte, Saisonarbeit)",
      "Vielseitige Tätigkeiten und Jobs mit schnellem Einstieg"
    ],
    questions: {
      q03: "Haben Sie bereits mit Grenzgängerstatus gearbeitet?",
      q04: "Welche maximale Fahrzeit würden Sie akzeptieren (einfache Strecke)?",
      q05: "Wie würden Sie sich täglich fortbewegen?",
      q06: "Wie sind Ihre zeitlichen Verfügbarkeiten?",
      q07: "Wählen Sie Ihre Verfügbarkeiten",
      q08: "Welche Vertragsarten würden Sie akzeptieren?",
      q09: "Ab wann wären Sie verfügbar, um eine Arbeit zu beginnen?",
      q10: "Wie weit sind Sie bei der Vorbereitung dieser Unterlagen?",
      q10Hint: "Es ist nicht nötig, bereits alle Unterlagen zu haben.",
      q11: "Haben Sie bereits eine luxemburgische Sozialversicherungsnummer oder Zugehörigkeit?",
      q12: "Haben Sie bereits eine deutsche Sozialversicherungsnummer oder Zugehörigkeit?",
      q13: "Haben Sie bereits eine französische Sozialversicherungsnummer oder Zugehörigkeit?",
      q14: "Haben Sie bereits in einem anderen Land gelebt und gearbeitet?",
      q15: "Wann möchten Sie aufbrechen?",
      q16: "Unter welchen Bedingungen würden Sie aufbrechen:",
      q18: "Ihre Sprachkenntnisse",
      q19: "In welchen Bereichen möchten Sie arbeiten?",
      sectorHint: "Sie können bis zu 4 Antworten auswählen.",
      q21: "Haben Sie Berufserfahrung im Verkauf und Handel?",
      q23: "Haben Sie Berufserfahrung in der Reinigung?",
      q24: "Verfügen Sie über einen Strafregisterauszug, der nicht älter als 3 Monate ist?",
      q26: "Haben Sie Berufserfahrung in Hotellerie und Gastronomie?",
      q28: "Haben Sie Berufserfahrung in Landwirtschaft und Ernte?",
      q30: "Haben Sie Berufserfahrung?",
      salaryType: "In welcher Form denken Sie an Ihr Gehalt?",
      salaryMin: "Was ist das Minimum, das Sie für diesen Beruf in Euro brutto oder netto erwarten würden?",
      firstName: "Vorname",
      lastName: "Nachname",
      email: "E-Mail-Adresse",
      phone: "Telefon",
      city: "Aktueller Wohnort",
      cv: "Möchten Sie Ihren Lebenslauf übermitteln?"
    },
    options: {
      yesNo: ["Ja", "Nein"],
      yesNoUnknown: ["Ja", "Nein", "Ich weiß es nicht"],
      commute: ["30 Min.", "1 Std.", "1 Std. 30", "2 Std.", "Mehr als 2 Std."],
      transport: ["Auto", "Zug", "Bus", "Fahrgemeinschaft", "Ich weiß es noch nicht"],
      schedule: ["Ich bin zu unterschiedlichen Zeiten verfügbar", "Ich habe zeitliche Einschränkungen oder Präferenzen"],
      contracts: ["Unbefristeter Vertrag", "Befristeter Vertrag", "Zeitarbeit", "Saisonarbeit", "Vollzeit", "Teilzeit"],
      startDate: ["So schnell wie möglich", "In den nächsten Tagen", "In den nächsten Wochen", "In 1 bis 3 Monaten", "Ich weiß es noch nicht"],
      departWhen: ["So schnell wie möglich", "Innerhalb von 3 Monaten", "Zwischen 3 und 6 Monaten", "In mehr als 6 Monaten", "Ich weiß es nicht"],
      departWith: ["Nur Sie", "Als Paar", "Als Familie"],
      experience: ["Ja, mehr als 2 Jahre", "Ja, zwischen 6 Monaten und 2 Jahren", "Ja, weniger als 6 Monate", "Nein, aber ich interessiere mich für diesen Bereich"],
      backgroundCheck: ["Ja", "Nein", "Ich kann ihn schnell beantragen", "Ich weiß es nicht"]
    },
    salaryUnits: ["Pro Stunde", "Pro Monat", "Pro Jahr"],
    salaryFields: {
      type: "In welcher Form denken Sie an Ihr Gehalt?",
      min: "Was ist das Minimum, das Sie für diesen Beruf in Euro brutto oder netto erwarten würden?"
    },
    sectorTitles: {
      vente: "Verkauf und Handel",
      nettoyage: "Reinigung und Instandhaltung",
      hotel: "Hotellerie und Gastronomie",
      agri: "Landwirtschaft und Ernte",
      polyvalent: "Vielseitige Tätigkeiten und Jobs mit schnellem Einstieg"
    },
    sectorLegends: {
      vente: "Verkauf und Handel: Welche der folgenden Aussagen passen am besten zu Ihnen?",
      nettoyage: "Reinigung und Instandhaltung: Welche der folgenden Aussagen passen am besten zu Ihnen?",
      hotel: "Hotellerie und Gastronomie: Welche der folgenden Aussagen passen am besten zu Ihnen?",
      agri: "Landwirtschaft und Ernte: Welche der folgenden Aussagen passen am besten zu Ihnen?",
      polyvalent: "Vielseitige Tätigkeiten und Jobs mit schnellem Einstieg: Welche der folgenden Aussagen passen am besten zu Ihnen?"
    },
    sectorChoices: {
      vente: ["Kunden empfangen und orientieren", "Zu einem Produkt oder einer Dienstleistung beraten", "Eine Anfrage schnell verstehen", "Eine Zahlung durchführen", "In Stoßzeiten ruhig bleiben", "Im Team arbeiten", "Pünktlich sein", "Sich an verschiedene Aufgaben anpassen", "Stress standhalten", "Bei Bedarf einem Kollegen helfen", "Kundschaft binden", "Einen Verkaufsbereich sauber und organisiert halten"],
      nettoyage: ["Selbstständig arbeiten", "Anweisungen befolgen", "Die eigene Arbeit organisieren", "Einen Bereich sauber und organisiert halten", "Sich an eine unvorhergesehene Situation anpassen", "Sorgfältig mit dem verwendeten Material umgehen", "In den Aufgaben effizient sein", "Im Team arbeiten", "Bei Bedarf einem Kollegen helfen", "Pünktlich sein", "Hygiene- und Sicherheitsregeln einhalten", "Wiederholende Aufgaben ausführen"],
      hotel: ["Kunden empfangen und orientieren", "Im Team arbeiten", "Während starker Auslastung ruhig bleiben", "Anweisungen befolgen", "Pünktlich sein", "Sich an verschiedene Aufgaben anpassen", "Bestellungen oder Informationen behalten", "Bei Bedarf einem Kollegen helfen", "Stress standhalten", "Einen Bereich sauber und organisiert halten", "Einen Kunden beraten oder auf eine Anfrage antworten"],
      agri: ["Pünktlich sein", "Im Team arbeiten", "Anweisungen befolgen", "Sorgfältig mit dem verwendeten Material umgehen", "Bei Bedarf einem Kollegen helfen", "In intensiven Arbeitsphasen ruhig bleiben", "Körperliche Aufgaben ausführen", "Im Freien und je nach Wetterbedingungen arbeiten", "Sich an verschiedene Aufgaben anpassen", "Wiederholende Aufgaben ausführen"],
      polyvalent: ["Sich schnell an eine neue Aufgabe anpassen", "Im Team arbeiten", "Anweisungen befolgen", "Arbeitszeiten einhalten", "Körperliche Arbeit ausführen", "In hohem Tempo arbeiten", "In unterschiedlichen Umgebungen arbeiten", "Variable Arbeitszeiten akzeptieren", "Bei Bedarf einem Kollegen helfen", "Schnell verfügbar sein"]
    }
  }
};

function localizeOptions(values, labels) {
  return values.map((value, index) => ({ value, label: labels[index] || value }));
}

function localizeRows(rows, labels) {
  return rows.map((row, index) => ({ ...row, label: labels[index] || row.label }));
}

function getCandidateTallyContent(lang) {
  const content = candidateTallyCopy[lang] || candidateTallyCopy.fr;
  return {
    ...content,
    mobilityTypeOptions: localizeOptions(candidateTallyMeta.mobilityTypes, content.mobilityTypeOptions),
    countryColumns: localizeOptions(candidateTallyMeta.countryColumns, content.countryColumns),
    countryRows: localizeRows(candidateTallyMeta.countryRows, content.countryRows),
    scheduleColumns: localizeOptions(candidateTallyMeta.scheduleColumns, content.scheduleColumns),
    scheduleRows: localizeRows(candidateTallyMeta.scheduleRows, content.scheduleRows),
    documentsColumns: localizeOptions(candidateTallyMeta.documentsColumns, content.documentsColumns),
    documentsRows: localizeRows(candidateTallyMeta.documentsRows, content.documentsRows),
    languageColumns: localizeOptions(candidateTallyMeta.languageColumns, content.languageColumns),
    languageRows: localizeRows(candidateTallyMeta.languageRows, content.languageRows),
    sectorsOptions: localizeOptions(candidateTallyMeta.sectors, content.sectors),
    rankingDisplayOptions: content.rankingOptions
  };
}

const employerTallyMeta = {
  formId: "ZjZA7A",
  sectors: [
    "Vente et commerce",
    "Nettoyage et entretien",
    "Hôtellerie et restauration",
    "Agriculture et récolte",
    "Missions polyvalentes et emplois accessibles rapidement"
  ],
  languageColumns: ["Pas nécessaire", "Communication simple", "Communication professionelle", "Très important au quotidien"],
  languageRows: [
    { field: "tally_q02_f01", label: "Allemand" },
    { field: "tally_q02_f02", label: "Anglais" },
    { field: "tally_q02_f03", label: "Français" },
    { field: "tally_q02_f04", label: "Luxembourgeois" }
  ],
  sectorPriorityGroups: {
    tally_q10: [
      "Être à l’aise avec les clients",
      "Pouvoir communiquer simplement avec les clients",
      "Travailler pendant les périodes d’affluence",
      "Réaliser des opérations d'encaissements",
      "Travailler en équipe",
      "S’adapter à différentes tâches",
      "Maintenir un espace de vente propre et organisé",
      "Respecter les horaires de travail"
    ],
    tally_q11: [
      "Respecter les procédures, consignes et les règles d’hygiène",
      "Maintenir un niveau de qualité constant",
      "Respecter les horaires de travail",
      "Travailler de manière autonome",
      "Travailler en équipe",
      "Travailler à un rythme soutenu",
      "S’adapter à différents lieux ou environnements de travail",
      "Réaliser des tâches répétitives",
      "Pouvoir se déplacer facilement sur les lieux d’intervention"
    ],
    tally_q12: [
      "Accueillir et orienter les clients",
      "Pouvoir communiquer simplement avec les clients",
      "Travailler pendant les périodes d’affluence",
      "Garder son calme en période d’activité intense",
      "Travailler en équipe",
      "Respecter les horaires de travail",
      "Travailler en soirée, le week-end ou les jours fériés",
      "Mémoriser des commandes ou des informations",
      "S’adapter à différentes tâches",
      "Maintenir un espace d'accueil ou de service propre et organisé"
    ],
    tally_q13: [
      "Respecter les horaires et les périodes de récolte",
      "Travailler en extérieur et selon les conditions météo",
      "Réaliser un travail physique",
      "Travailler à un rythme soutenu",
      "Respecter les consignes de travail et de sécurité",
      "Utiliser correctement le matériel ou les outils",
      "Travailler en équipe",
      "S’adapter à différents types de travaux",
      "Pouvoir se déplacer facilement sur les lieux de travail",
      "Maintenir une qualité de travail régulière"
    ],
    tally_q14: [
      "S’adapter rapidement à différentes tâches",
      "Respecter les consignes et les horaires",
      "Réaliser un travail physique",
      "Travailler à un rythme soutenu",
      "Travailler dans différents environnements",
      "Intégrer rapidement une équipe",
      "Travailler en équipe",
      "Accepter des horaires variables",
      "Être disponible rapidement",
      "Pouvoir commencer rapidement une mission"
    ]
  }
};

const employerTallyCopy = {
  fr: {
    eyebrow: "Questionnaire employeur EURES",
    heroTitle: "Décrire un besoin de recrutement ouvert à la mobilité européenne",
    heroLede: "Ce questionnaire nous aide à mieux comprendre votre besoin de recrutement, les profils recherchés, les langues utiles et les conditions de travail proposées.",
    heroHighlight: "L’objectif est de rendre votre besoin plus clair et plus comparable, pour faciliter ensuite l’identification de profils compatibles.",
    sidebarWhyTitle: "Pourquoi ce questionnaire ?",
    sidebarWhyText: "Il sert à rendre le besoin de recrutement plus lisible : secteur, volume, langues, contraintes de travail, profils acceptés et éventuelles aides à l’installation.",
    sidebarAfterTitle: "Et après ?",
    sidebarAfterText: "Si des profils semblent correspondre, votre besoin peut être repris pour une mise en relation. Sinon, les réponses servent déjà à mieux structurer les prochains recrutements.",
    sidebarResumeTitle: "Reprendre plus tard",
    sidebarResumeText: "Un identifiant est conservé pour retrouver votre progression si besoin.",
    salaryOfferIntro: "Indiquez ici le salaire proposé pour ce métier, en euros, en précisant s'il s'agit d'un montant brut ou net.",
    introNote: "Ce formulaire prend 2 à 3 minutes et s’adresse aux employeurs ayant des besoins de recrutement ouverts à la mobilité européenne et aux recrutements hors frontières.",
    introNote2: "Nous travaillons actuellement sur quelques métiers prioritaires, afin de tester le service sur des cas concrets.",
    matrixMobileHint: "Sur téléphone et tablette, chaque ligne s'affiche verticalement pour faciliter la lecture.",
    sections: {
      need: "Votre besoin de recrutement",
      conditions: "Profils, aides et conditions de travail",
      contact: "Pour pouvoir vous recontacter"
    },
    questions: {
      q01: "Dans quel secteur recrutez-vous actuellement ?",
      q02: "Quelles langues sont impératives pour ce recrutement ?",
      q02Hint: "Indiquez le niveau de communication attendu pour chaque langue.",
      q03: "Combien de personnes souhaitez-vous recruter ?",
      q04: "À partir de quand avez-vous besoin de ces recrutements ?",
      q05: "Quelle durée de contrat proposez-vous ?",
      q06: "Quel volume de travail hebdomadaire proposez-vous ?",
      q07: "Quels profils êtes-vous prêts à recruter ?",
      q08: "Pouvez-vous aider les personnes recrutées dans leur arrivée ou leur installation ?",
      q09: "Parmi les éléments suivants, lesquels sont indispensables pour vous ?",
      q10: "Pour ce recrutement en vente et commerce, quels éléments vous semblent les plus importants ?",
      q11: "Pour ce recrutement en nettoyage et entretien, quels éléments vous semblent les plus importants ?",
      q12: "Pour ce recrutement en hôtellerie et restauration, quels éléments vous semblent les plus importants ?",
      q13: "Pour ce recrutement en agriculture et récolte, quels éléments vous semblent les plus importants ?",
      q14: "Pour ce recrutement en missions polyvalentes et emplois accessibles rapidement, quels éléments vous semblent les plus importants ?",
      q14Hint: "Vous pouvez sélectionner jusqu'à 4 propositions.",
      q15: "Quelles conditions de travail les personnes recrutées doivent-elles connaître ?",
      q16: "Prénom",
      q17: "Nom de l'entreprise",
      q18: "Adresse e-mail",
      q19: "Téléphone",
      q20: "Lieux de travail",
      q20Extra: "Quels autres métiers souhaiteriez-vous voir proposés ici à l'avenir ?",
      salaryType: "Sous quelle forme exprimez-vous le salaire proposé ?",
      salaryMin: "Montant minimum proposé, en euros bruts ou nets",
      salaryMax: "Montant maximum proposé, en euros bruts ou nets",
      q21Title: "Protection des données",
      q21Text: "Les informations transmises permettront à l’équipe EURES beta de mieux comprendre votre besoin de recrutement et les conditions proposées afin d’identifier des profils susceptibles de correspondre.",
      q21Text2: "Si des profils compatibles avec votre recherche sont identifiés, vous pourrez être recontacté prochainement.",
      q21Text3: "Pensez à répondre aux appels masqués ou inconnus et à vérifier régulièrement vos courriers indésirables (spams).",
      consent: "J’accepte que les informations transmises soient utilisées par les équipes et partenaires EURES dans le cadre des mises en relation et des échanges liés au recrutement. Les données transmises seront utilisées uniquement dans le cadre des échanges liés au recrutement et conformément à la réglementation européenne sur la protection des données (RGPD)."
    },
    options: {
      sectors: employerTallyMeta.sectors,
      q03: ["1 personne", "2 à 5 personnes", "Plus de 5 personnes", "Je ne sais pas encore"],
      q04: ["Dès que possible", "Dans les prochains jours", "Dans les prochaines semaines", "Pour une période saisonnière", "Je ne sais pas encore"],
      q05: ["Moins d'un mois", "1 à 3 mois", "3 à 6 mois", "Plus de 6 mois", "Contrat sans date de fin prévue", "Je ne sais pas encore"],
      q06: ["Moins de 20 heures par semaine", "20 à 34 heures par semaine", "35 heures ou plus par semaine", "Le volume peut varier selon l'activité", "Je ne sais pas encore"],
      q07: ["Des travailleurs frontaliers", "Des personnes venant d’un autre pays de l’Union européenne", "Des personnes débutantes dans le métier", "Des personnes ayant besoin de temps pour s’installer", "Des personnes ne parlant pas encore parfaitement la langue", "Je ne sais pas encore"],
      q08: ["Oui, pour le logement", "Oui, pour les démarches administratives", "Oui, pour les transports ou déplacement", "Non", "Je ne sais pas encore"],
      q09: ["Une expérience dans le métier", "Une disponibilité rapide", "Le permis de conduire", "Une expérience de travail dans le pays", "Aucun de ces éléments n'est indispensable", "La motivation pour le poste", "Je ne sais pas encore"],
      q15: ["Travail tôt le matin ou en horaire décalés", "Travail en soirée ou la nuit", "Travail le week-end ou les jours fériés", "Horaires variables", "Travail physique", "Travail debout prolongé", "Travail en extérieur", "Déplacement fréquents", "Travail en équipe", "Aucune condition particulière", "Je ne sais pas encore"]
    },
    salaryUnits: ["Par heure", "Par mois", "Par an"],
    salaryFields: {
      type: "Sous quelle forme exprimez-vous le salaire proposé ?",
      min: "Montant minimum proposé, en euros bruts ou nets",
      max: "Montant maximum proposé, en euros bruts ou nets"
    },
    sectorTitles: {
      tally_q10: "Vente et commerce",
      tally_q11: "Nettoyage et entretien",
      tally_q12: "Hôtellerie et restauration",
      tally_q13: "Agriculture et récolte",
      tally_q14: "Missions polyvalentes et emplois accessibles rapidement"
    },
    errors: {
      chooseAtLeastOne: "Sélectionnez au moins une réponse pour :",
      chooseBetween: "Sélectionnez entre 1 et 4 réponses pour :",
      maxFour: "Vous avez déjà choisi 4 éléments pour cette section."
    }
  },
  en: {
    eyebrow: "EURES employer questionnaire",
    heroTitle: "Describe a hiring need open to European mobility",
    heroLede: "This questionnaire helps us better understand your hiring need, the profiles you are looking for, the useful languages and the working conditions you offer.",
    heroHighlight: "The aim is to make your need clearer and more comparable, so that compatible profiles can be identified more easily afterwards.",
    sidebarWhyTitle: "Why this questionnaire?",
    sidebarWhyText: "It makes the hiring need easier to read: sector, volume, languages, working constraints, accepted profiles and possible relocation support.",
    sidebarAfterTitle: "What happens next?",
    sidebarAfterText: "If some profiles seem compatible, your need can be used for an introduction. Otherwise, the answers already help us structure future recruitments better.",
    sidebarResumeTitle: "Continue later",
    sidebarResumeText: "An identifier is kept so your progress can be found again if needed.",
    salaryOfferIntro: "Indicate the salary offered for this role here, in euros, and specify whether it is gross or net.",
    introNote: "This form takes 2 to 3 minutes and is intended for employers with hiring needs open to European mobility and cross-border recruitment.",
    introNote2: "We are currently working on a few priority occupations in order to test the service on concrete cases.",
    matrixMobileHint: "On mobile and tablet, each row is displayed vertically for easier reading.",
    sections: {
      need: "Your hiring need",
      conditions: "Profiles, support and working conditions",
      contact: "So that we can contact you again"
    },
    questions: {
      q01: "In which sector are you currently recruiting?",
      q02: "Which languages are essential for this recruitment?",
      q02Hint: "Indicate the expected level of communication for each language.",
      q03: "How many people would you like to recruit?",
      q04: "From when do you need these recruitments?",
      q05: "What contract duration do you offer?",
      q06: "What weekly working volume do you offer?",
      q07: "Which profiles are you ready to recruit?",
      q08: "Can you help recruited people with their arrival or settlement?",
      q09: "Which of the following elements are essential for you?",
      q10: "For this sales and retail recruitment, which elements seem most important to you?",
      q11: "For this cleaning and maintenance recruitment, which elements seem most important to you?",
      q12: "For this hospitality and food service recruitment, which elements seem most important to you?",
      q13: "For this agriculture and harvesting recruitment, which elements seem most important to you?",
      q14: "For this versatile jobs and quick-access roles recruitment, which elements seem most important to you?",
      q14Hint: "You can select up to 4 options.",
      q15: "Which working conditions should recruited people be aware of?",
      q16: "First name",
      q17: "Company name",
      q18: "Email address",
      q19: "Phone",
      q20: "Work locations",
      q20Extra: "Which other occupations would you like to see included here in the future?",
      salaryType: "How do you express the salary offered?",
      salaryMin: "Minimum amount offered, in gross or net euros",
      salaryMax: "Maximum amount offered, in gross or net euros",
      q21Title: "Data protection",
      q21Text: "The information provided will allow the EURES beta team to better understand your hiring need and the conditions offered in order to identify profiles that may match.",
      q21Text2: "If profiles compatible with your search are identified, you may be contacted again soon.",
      q21Text3: "Please remember to answer hidden or unknown calls and to check your junk mail regularly.",
      consent: "I agree that the information provided may be used by EURES teams and partners for introductions and exchanges related to recruitment. The data provided will only be used within the framework of recruitment exchanges and in accordance with European data protection rules (GDPR)."
    },
    options: {
      sectors: ["Sales and retail", "Cleaning and maintenance", "Hospitality and food service", "Agriculture and harvesting", "Versatile jobs and roles accessible quickly"],
      q02Columns: ["Not necessary", "Simple communication", "Professional communication", "Very important on a daily basis"],
      q02Rows: ["German", "English", "French", "Luxembourgish"],
      q03: ["1 person", "2 to 5 people", "More than 5 people", "I do not know yet"],
      q04: ["As soon as possible", "In the next few days", "In the next few weeks", "For a seasonal period", "I do not know yet"],
      q05: ["Less than one month", "1 to 3 months", "3 to 6 months", "More than 6 months", "Contract with no planned end date", "I do not know yet"],
      q06: ["Less than 20 hours per week", "20 to 34 hours per week", "35 hours or more per week", "The workload may vary depending on activity", "I do not know yet"],
      q07: ["Cross-border workers", "People coming from another European Union country", "People who are beginners in the profession", "People who need time to settle in", "People who do not yet speak the language perfectly", "I do not know yet"],
      q08: ["Yes, for housing", "Yes, for administrative procedures", "Yes, for transport or travel", "No", "I do not know yet"],
      q09: ["Experience in the profession", "Quick availability", "Driving licence", "Work experience in the country", "None of these elements is essential", "Motivation for the role", "I do not know yet"],
      q15: ["Early morning work or staggered hours", "Evening or night work", "Weekend or public holiday work", "Variable hours", "Physical work", "Prolonged standing work", "Outdoor work", "Frequent travel", "Teamwork", "No particular condition", "I do not know yet"]
    },
    salaryUnits: ["Per hour", "Per month", "Per year"],
    salaryFields: {
      type: "How do you express the salary offered?",
      min: "Minimum amount offered, in gross or net euros",
      max: "Maximum amount offered, in gross or net euros"
    },
    sectorTitles: {
      tally_q10: "Sales and retail",
      tally_q11: "Cleaning and maintenance",
      tally_q12: "Hospitality and food service",
      tally_q13: "Agriculture and harvesting",
      tally_q14: "Versatile jobs and roles accessible quickly"
    },
    sectorChoices: {
      tally_q10: ["Being comfortable with customers", "Being able to communicate simply with customers", "Working during busy periods", "Handling payment operations", "Working as part of a team", "Adapting to different tasks", "Keeping a sales area clean and organised", "Respecting working hours"],
      tally_q11: ["Following procedures, instructions and hygiene rules", "Maintaining a consistent level of quality", "Respecting working hours", "Working independently", "Working as part of a team", "Working at a sustained pace", "Adapting to different workplaces or environments", "Carrying out repetitive tasks", "Being able to travel easily to intervention sites"],
      tally_q12: ["Welcoming and guiding customers", "Being able to communicate simply with customers", "Working during busy periods", "Staying calm during intense periods of activity", "Working as part of a team", "Respecting working hours", "Working in the evening, on weekends or on public holidays", "Remembering orders or information", "Adapting to different tasks", "Keeping a reception or service area clean and organised"],
      tally_q13: ["Respecting schedules and harvesting periods", "Working outdoors and depending on weather conditions", "Doing physical work", "Working at a sustained pace", "Following work and safety instructions", "Using equipment or tools correctly", "Working as part of a team", "Adapting to different types of tasks", "Being able to travel easily to work sites", "Maintaining a consistent quality of work"],
      tally_q14: ["Adapting quickly to different tasks", "Respecting instructions and schedules", "Doing physical work", "Working at a sustained pace", "Working in different environments", "Joining a team quickly", "Working as part of a team", "Accepting variable schedules", "Being available quickly", "Being able to start an assignment quickly"]
    },
    errors: {
      chooseAtLeastOne: "Select at least one answer for:",
      chooseBetween: "Select between 1 and 4 answers for:",
      maxFour: "You have already selected 4 items for this section."
    }
  },
  de: {
    eyebrow: "EURES-Arbeitgeberfragebogen",
    heroTitle: "Einen Personalbedarf beschreiben, der für europäische Mobilität offen ist",
    heroLede: "Dieser Fragebogen hilft uns, Ihren Personalbedarf, die gesuchten Profile, die nützlichen Sprachen und die angebotenen Arbeitsbedingungen besser zu verstehen.",
    heroHighlight: "Ziel ist es, Ihren Bedarf klarer und besser vergleichbar zu machen, damit anschließend passende Profile leichter erkannt werden können.",
    sidebarWhyTitle: "Warum dieser Fragebogen?",
    sidebarWhyText: "Er macht den Personalbedarf besser lesbar: Bereich, Volumen, Sprachen, Arbeitsbedingungen, akzeptierte Profile und mögliche Unterstützung bei der Installation.",
    sidebarAfterTitle: "Wie geht es danach weiter?",
    sidebarAfterText: "Wenn einige Profile kompatibel erscheinen, kann Ihr Bedarf für eine Vermittlung genutzt werden. Andernfalls helfen die Antworten bereits dabei, künftige Einstellungen besser zu strukturieren.",
    sidebarResumeTitle: "Später fortsetzen",
    sidebarResumeText: "Eine Kennung wird gespeichert, damit Ihr Fortschritt bei Bedarf wiedergefunden werden kann.",
    salaryOfferIntro: "Geben Sie hier das für diesen Beruf angebotene Gehalt in Euro an und präzisieren Sie, ob es sich um einen Brutto- oder Nettobetrag handelt.",
    introNote: "Dieses Formular dauert 2 bis 3 Minuten und richtet sich an Arbeitgeber mit Personalbedarf, der für europäische Mobilität und grenzüberschreitende Rekrutierung offen ist.",
    introNote2: "Wir arbeiten derzeit an einigen prioritären Berufen, um den Dienst an konkreten Fällen zu testen.",
    matrixMobileHint: "Auf Smartphone und Tablet wird jede Zeile untereinander angezeigt, damit sie leichter lesbar ist.",
    sections: {
      need: "Ihr Personalbedarf",
      conditions: "Profile, Unterstützung und Arbeitsbedingungen",
      contact: "Damit wir Sie wieder kontaktieren können"
    },
    questions: {
      q01: "In welchem Bereich rekrutieren Sie derzeit?",
      q02: "Welche Sprachen sind für diese Rekrutierung zwingend erforderlich?",
      q02Hint: "Geben Sie das erwartete Kommunikationsniveau für jede Sprache an.",
      q03: "Wie viele Personen möchten Sie einstellen?",
      q04: "Ab wann benötigen Sie diese Einstellungen?",
      q05: "Welche Vertragsdauer bieten Sie an?",
      q06: "Welches wöchentliche Arbeitsvolumen bieten Sie an?",
      q07: "Welche Profile sind Sie bereit einzustellen?",
      q08: "Können Sie den eingestellten Personen bei ihrer Ankunft oder Installation helfen?",
      q09: "Welche der folgenden Elemente sind für Sie unverzichtbar?",
      q10: "Welche Elemente erscheinen Ihnen bei dieser Einstellung im Verkauf und Handel am wichtigsten?",
      q11: "Welche Elemente erscheinen Ihnen bei dieser Einstellung in Reinigung und Instandhaltung am wichtigsten?",
      q12: "Welche Elemente erscheinen Ihnen bei dieser Einstellung in Hotellerie und Gastronomie am wichtigsten?",
      q13: "Welche Elemente erscheinen Ihnen bei dieser Einstellung in Landwirtschaft und Ernte am wichtigsten?",
      q14: "Welche Elemente erscheinen Ihnen bei dieser Einstellung für vielseitige Tätigkeiten und schnell zugängliche Jobs am wichtigsten?",
      q14Hint: "Sie können bis zu 4 Antworten auswählen.",
      q15: "Welche Arbeitsbedingungen sollten die eingestellten Personen kennen?",
      q16: "Vorname",
      q17: "Unternehmensname",
      q18: "E-Mail-Adresse",
      q19: "Telefon",
      q20: "Arbeitsorte",
      q20Extra: "Welche anderen Berufe würden Sie hier künftig gerne sehen?",
      salaryType: "In welcher Form geben Sie das angebotene Gehalt an?",
      salaryMin: "Angebotener Mindestbetrag in Euro brutto oder netto",
      salaryMax: "Angebotener Höchstbetrag in Euro brutto oder netto",
      q21Title: "Datenschutz",
      q21Text: "Die übermittelten Informationen ermöglichen es dem EURES-beta-Team, Ihren Personalbedarf und die angebotenen Bedingungen besser zu verstehen, um Profile zu identifizieren, die passen könnten.",
      q21Text2: "Wenn mit Ihrer Suche kompatible Profile identifiziert werden, können Sie in Kürze erneut kontaktiert werden.",
      q21Text3: "Bitte denken Sie daran, anonyme oder unbekannte Anrufe anzunehmen und regelmäßig Ihren Spam-Ordner zu prüfen.",
      consent: "Ich stimme zu, dass die übermittelten Informationen von EURES-Teams und Partnern im Rahmen von Vermittlungen und austauschbezogenen Rekrutierungen verwendet werden dürfen. Die übermittelten Daten werden nur im Rahmen des recruitmentbezogenen Austauschs und gemäß den europäischen Datenschutzvorschriften (DSGVO) verwendet."
    },
    options: {
      sectors: ["Verkauf und Handel", "Reinigung und Instandhaltung", "Hotellerie und Gastronomie", "Landwirtschaft und Ernte", "Vielseitige Tätigkeiten und Jobs mit schnellem Einstieg"],
      q02Columns: ["Nicht erforderlich", "Einfache Kommunikation", "Berufliche Kommunikation", "Im Alltag sehr wichtig"],
      q02Rows: ["Deutsch", "Englisch", "Französisch", "Luxemburgisch"],
      q03: ["1 Person", "2 bis 5 Personen", "Mehr als 5 Personen", "Ich weiß es noch nicht"],
      q04: ["So schnell wie möglich", "In den nächsten Tagen", "In den nächsten Wochen", "Für einen saisonalen Zeitraum", "Ich weiß es noch nicht"],
      q05: ["Weniger als ein Monat", "1 bis 3 Monate", "3 bis 6 Monate", "Mehr als 6 Monate", "Vertrag ohne geplantes Enddatum", "Ich weiß es noch nicht"],
      q06: ["Weniger als 20 Stunden pro Woche", "20 bis 34 Stunden pro Woche", "35 Stunden oder mehr pro Woche", "Das Arbeitsvolumen kann je nach Aktivität variieren", "Ich weiß es noch nicht"],
      q07: ["Grenzgänger", "Personen aus einem anderen Land der Europäischen Union", "Berufseinsteiger", "Personen, die Zeit für die Installation brauchen", "Personen, die die Sprache noch nicht perfekt sprechen", "Ich weiß es noch nicht"],
      q08: ["Ja, beim Wohnen", "Ja, bei administrativen Verfahren", "Ja, bei Transport oder Fahrten", "Nein", "Ich weiß es noch nicht"],
      q09: ["Berufserfahrung", "Schnelle Verfügbarkeit", "Führerschein", "Arbeitserfahrung im Land", "Keines dieser Elemente ist unverzichtbar", "Motivation für die Stelle", "Ich weiß es noch nicht"],
      q15: ["Arbeit früh am Morgen oder zu versetzten Zeiten", "Arbeit am Abend oder in der Nacht", "Arbeit am Wochenende oder an Feiertagen", "Variable Arbeitszeiten", "Körperliche Arbeit", "Längeres Stehen", "Arbeit im Freien", "Häufige Fahrten", "Teamarbeit", "Keine besonderen Bedingungen", "Ich weiß es noch nicht"]
    },
    salaryUnits: ["Pro Stunde", "Pro Monat", "Pro Jahr"],
    salaryFields: {
      type: "In welcher Form geben Sie das angebotene Gehalt an?",
      min: "Angebotener Mindestbetrag in Euro brutto oder netto",
      max: "Angebotener Höchstbetrag in Euro brutto oder netto"
    },
    sectorTitles: {
      tally_q10: "Verkauf und Handel",
      tally_q11: "Reinigung und Instandhaltung",
      tally_q12: "Hotellerie und Gastronomie",
      tally_q13: "Landwirtschaft und Ernte",
      tally_q14: "Vielseitige Tätigkeiten und Jobs mit schnellem Einstieg"
    },
    sectorChoices: {
      tally_q10: ["Sich im Umgang mit Kunden wohlfühlen", "Einfach mit Kunden kommunizieren können", "Während Stoßzeiten arbeiten", "Kassenvorgänge durchführen", "Im Team arbeiten", "Sich an verschiedene Aufgaben anpassen", "Einen Verkaufsbereich sauber und organisiert halten", "Arbeitszeiten einhalten"],
      tally_q11: ["Verfahren, Anweisungen und Hygieneregeln einhalten", "Ein gleichbleibendes Qualitätsniveau halten", "Arbeitszeiten einhalten", "Selbstständig arbeiten", "Im Team arbeiten", "In hohem Tempo arbeiten", "Sich an verschiedene Arbeitsorte oder Umgebungen anpassen", "Wiederholende Aufgaben ausführen", "Einsatzorte leicht erreichen können"],
      tally_q12: ["Kunden empfangen und orientieren", "Einfach mit Kunden kommunizieren können", "Während Stoßzeiten arbeiten", "In intensiven Phasen ruhig bleiben", "Im Team arbeiten", "Arbeitszeiten einhalten", "Abends, am Wochenende oder an Feiertagen arbeiten", "Bestellungen oder Informationen behalten", "Sich an verschiedene Aufgaben anpassen", "Einen Empfangs- oder Servicebereich sauber und organisiert halten"],
      tally_q13: ["Zeitpläne und Erntezeiten einhalten", "Im Freien und je nach Wetter arbeiten", "Körperliche Arbeit leisten", "In hohem Tempo arbeiten", "Arbeits- und Sicherheitsanweisungen einhalten", "Material oder Werkzeuge korrekt verwenden", "Im Team arbeiten", "Sich an unterschiedliche Arten von Aufgaben anpassen", "Arbeitsorte leicht erreichen können", "Eine gleichbleibende Arbeitsqualität aufrechterhalten"],
      tally_q14: ["Sich schnell an verschiedene Aufgaben anpassen", "Anweisungen und Zeitpläne einhalten", "Körperliche Arbeit leisten", "In hohem Tempo arbeiten", "In unterschiedlichen Umgebungen arbeiten", "Sich schnell in ein Team integrieren", "Im Team arbeiten", "Variable Arbeitszeiten akzeptieren", "Schnell verfügbar sein", "Schnell eine Aufgabe beginnen können"]
    },
    errors: {
      chooseAtLeastOne: "Wählen Sie mindestens eine Antwort für:",
      chooseBetween: "Wählen Sie zwischen 1 und 4 Antworten für:",
      maxFour: "Sie haben für diesen Abschnitt bereits 4 Elemente ausgewählt."
    }
  }
};

function getEmployerTallyContent(lang) {
  const content = employerTallyCopy[lang] || employerTallyCopy.fr;
  const frContent = employerTallyCopy.fr;
  return {
    ...content,
    sectorsOptions: localizeOptions(employerTallyMeta.sectors, content.options.sectors || frContent.options.sectors || employerTallyMeta.sectors),
    languageColumns: localizeOptions(
      employerTallyMeta.languageColumns,
      content.options.q02Columns || frContent.options.q02Columns || employerTallyMeta.languageColumns
    ),
    languageRows: localizeRows(
      employerTallyMeta.languageRows,
      content.options.q02Rows || frContent.options.q02Rows || employerTallyMeta.languageRows.map((row) => row.label)
    ),
    optionGroups: {
      q03: localizeOptions(frContent.options.q03, content.options.q03 || frContent.options.q03),
      q04: localizeOptions(frContent.options.q04, content.options.q04 || frContent.options.q04),
      q05: localizeOptions(frContent.options.q05, content.options.q05 || frContent.options.q05),
      q06: localizeOptions(frContent.options.q06, content.options.q06 || frContent.options.q06),
      q07: localizeOptions(frContent.options.q07, content.options.q07 || frContent.options.q07),
      q08: localizeOptions(frContent.options.q08, content.options.q08 || frContent.options.q08),
      q09: localizeOptions(frContent.options.q09, content.options.q09 || frContent.options.q09),
      q15: localizeOptions(frContent.options.q15, content.options.q15 || frContent.options.q15)
    },
    sectorPriorityOptions: Object.fromEntries(
      Object.entries(employerTallyMeta.sectorPriorityGroups).map(([key, value]) => [
        key,
        localizeOptions(value, (content.sectorChoices && content.sectorChoices[key]) || value)
      ])
    )
  };
}

function currentLang() {
  const params = new URLSearchParams(window.location.search);
  const lang = params.get("lang");
  return LANGS.includes(lang) ? lang : DEFAULT_LANG;
}

function currentInviteToken() {
  const params = new URLSearchParams(window.location.search);
  const inviteToken = (params.get("invite_token") || "").trim();
  return inviteToken || "";
}

function setDocumentLang(lang) {
  document.documentElement.lang = lang;
}

function pageUrl(page, lang) {
  const map = {
    home: `${BASE_PATH}/`,
    "candidate-landing": `${BASE_PATH}/candidate`,
    "employer-landing": `${BASE_PATH}/employer`,
    stat: `${BASE_PATH}/stat`,
    "candidate-questionnaire": `${BASE_PATH}/questionnaire-candidate`,
    "employer-questionnaire": `${BASE_PATH}/questionnaire-employer`
  };
  const params = new URLSearchParams({ lang });
  const inviteToken = currentInviteToken();
  if (inviteToken) {
    params.set("invite_token", inviteToken);
  }
  return `${map[page]}?${params.toString()}`;
}

function isVisibleControl(element) {
  if (!element || element.disabled) {
    return false;
  }
  if (element.closest("[hidden]")) {
    return false;
  }
  return element.getClientRects().length > 0;
}

function cleanLabelText(value) {
  return String(value || "")
    .replace(/\s+/g, " ")
    .replace(/\*/g, "")
    .trim();
}

function getFieldLabel(element) {
  if (!element) {
    return "";
  }

  const fromAria = cleanLabelText(element.getAttribute("aria-label"));
  if (fromAria) {
    return fromAria;
  }

  if (element.id) {
    const explicit = document.querySelector(`label[for="${CSS.escape(element.id)}"]`);
    const explicitText = cleanLabelText(explicit?.textContent);
    if (explicitText) {
      return explicitText;
    }
  }

  const field = element.closest(".field, .field-stack, .question-block, fieldset, .panel");
  const scopedLabel = cleanLabelText(
    field?.querySelector(":scope > span, :scope > legend, :scope > h3, :scope > h4, :scope > .section-title")?.textContent
  ) || cleanLabelText(
    field?.querySelector("legend, h3, h4, .section-title, span, label")?.textContent
  );
  if ((element.type === "radio" || element.type === "checkbox") && scopedLabel) {
    return scopedLabel;
  }

  const wrappingLabel = element.closest("label");
  const wrappingText = cleanLabelText(wrappingLabel?.textContent);
  if (wrappingText) {
    return wrappingText;
  }

  if (scopedLabel) {
    return scopedLabel;
  }

  return cleanLabelText(element.name || element.type || "champ");
}

function focusField(element) {
  if (!element) {
    return;
  }
  element.focus({ preventScroll: true });
  element.scrollIntoView({ behavior: "smooth", block: "center" });
}

function setStatusMessage(statusEl, message, state = "") {
  if (!statusEl) {
    return;
  }
  statusEl.textContent = message;
  statusEl.dataset.state = state;
  if (state === "error") {
    statusEl.setAttribute("role", "alert");
    statusEl.setAttribute("aria-live", "assertive");
  } else {
    statusEl.setAttribute("role", "status");
    statusEl.setAttribute("aria-live", "polite");
  }
}

function getFieldContainer(element) {
  return element?.closest(".field, .fieldset, .matrix-question, .matrix-wrap, .form-section") || null;
}

function nextFieldErrorId() {
  nextFieldErrorId.counter = (nextFieldErrorId.counter || 0) + 1;
  return `field-error-${nextFieldErrorId.counter}`;
}

function clearFieldErrorState(element) {
  if (!(element instanceof HTMLElement)) {
    return;
  }
  const container = getFieldContainer(element);
  if (container) {
    container.classList.remove("is-invalid");
    container.querySelectorAll(".field-error").forEach((node) => node.remove());
  }
  const controls = [];
  if (element instanceof HTMLInputElement && element.name) {
    controls.push(...document.querySelectorAll(`[name="${CSS.escape(element.name)}"]`));
  } else {
    controls.push(element);
  }
  controls.forEach((control) => {
    if (!(control instanceof HTMLElement)) {
      return;
    }
    control.removeAttribute("aria-invalid");
    const describedBy = String(control.getAttribute("aria-describedby") || "")
      .split(/\s+/)
      .filter((token) => token && !token.startsWith("field-error-"));
    if (describedBy.length) {
      control.setAttribute("aria-describedby", describedBy.join(" "));
    } else {
      control.removeAttribute("aria-describedby");
    }
  });
}

function clearInvalidState(scope) {
  const root = scope instanceof HTMLElement ? scope : document;
  root.querySelectorAll('[aria-invalid="true"]').forEach((node) => {
    node.removeAttribute("aria-invalid");
    const describedBy = String(node.getAttribute("aria-describedby") || "")
      .split(/\s+/)
      .filter((token) => token && !token.startsWith("field-error-"));
    if (describedBy.length) {
      node.setAttribute("aria-describedby", describedBy.join(" "));
    } else {
      node.removeAttribute("aria-describedby");
    }
  });
  root.querySelectorAll(".is-invalid").forEach((node) => node.classList.remove("is-invalid"));
  root.querySelectorAll(".field-error").forEach((node) => node.remove());
}

function setInlineFieldError(element, message) {
  const container = getFieldContainer(element);
  if (!container) {
    return;
  }
  container.classList.add("is-invalid");
  const existing = container.querySelector(".field-error");
  if (existing) {
    existing.textContent = message;
    return;
  }
  const note = document.createElement("p");
  note.className = "field-error";
  note.id = nextFieldErrorId();
  note.textContent = message;
  container.appendChild(note);
  const controls = [];
  if (element instanceof HTMLInputElement && element.name) {
    controls.push(...document.querySelectorAll(`[name="${CSS.escape(element.name)}"]`));
  } else {
    controls.push(element);
  }
  controls.forEach((control) => {
    if (!(control instanceof HTMLElement)) {
      return;
    }
    control.setAttribute("aria-invalid", "true");
    const describedBy = new Set(
      String(control.getAttribute("aria-describedby") || "")
        .split(/\s+/)
        .filter(Boolean)
    );
    describedBy.add(note.id);
    control.setAttribute("aria-describedby", Array.from(describedBy).join(" "));
  });
}

function describeInvalidField(element, t) {
  const label = getFieldLabel(element);
  if (element.validity?.valueMissing) {
    return `${t.common.validation.required} ${label}`;
  }
  if (element.validity?.typeMismatch && element.type === "email") {
    return `${t.common.validation.invalidEmail} ${label}`;
  }
  return `${t.common.validation.invalidValue} ${label}`;
}

function findFirstInvalidControl(form) {
  const seenRadioNames = new Set();
  const controls = Array.from(form.elements).filter((element) => {
    if (!(element instanceof HTMLElement)) {
      return false;
    }
    if (element.tagName === "BUTTON" || element.type === "hidden") {
      return false;
    }
    if (!isVisibleControl(element)) {
      return false;
    }
    if (element.type === "radio") {
      if (seenRadioNames.has(element.name)) {
        return false;
      }
      seenRadioNames.add(element.name);
    }
    return typeof element.checkValidity === "function" && !element.checkValidity();
  });

  return controls[0] || null;
}

function showFirstInvalidControl(form, setStatus, t) {
  clearInvalidState(form);
  const invalid = findFirstInvalidControl(form);
  if (!invalid) {
    return false;
  }

  const message = `${describeInvalidField(invalid, t)} ${t.common.validation.checkHighlighted}`;
  setStatus(message, "error");
  setInlineFieldError(invalid, message);
  focusField(invalid);
  if (typeof invalid.reportValidity === "function") {
    invalid.reportValidity();
  }
  return true;
}

function validateVisibleCheckboxGroup(form, name, label, setStatus, t, min = 1, max = Infinity) {
  clearInvalidState(form.querySelector(`input[name="${name}"]`) || form);
  const visibleInputs = Array.from(form.querySelectorAll(`input[name="${name}"]`)).filter((input) => isVisibleControl(input));
  if (!visibleInputs.length) {
    return true;
  }

  const checkedCount = visibleInputs.filter((input) => input.checked).length;
  if (checkedCount < min) {
    const message = `${t.common.validation.required} ${label}. ${t.common.validation.checkHighlighted}`;
    setStatus(message, "error");
    setInlineFieldError(visibleInputs[0], message);
    focusField(visibleInputs[0]);
    return false;
  }
  if (checkedCount > max) {
    const message = `${t.common.validation.invalidValue} ${label}. ${t.common.validation.checkHighlighted}`;
    setStatus(message, "error");
    setInlineFieldError(visibleInputs[0], message);
    focusField(visibleInputs[0]);
    return false;
  }
  return true;
}

function navSectionPage(page) {
  if (page === "candidate-questionnaire") {
    return "candidate-landing";
  }
  if (page === "employer-questionnaire") {
    return "employer-landing";
  }
  return page;
}

function nav(page, lang, t) {
  const currentPage = navSectionPage(page);
  const navItems = [
    ["home", t.common.navHome],
    ["candidate-landing", t.common.navCandidate],
    ["employer-landing", t.common.navEmployer],
    ["stat", t.common.navStats],
  ];
  return `
    <a class="skip-link" href="#main-content">Aller au contenu</a>
    <header class="site-header">
      <div class="shell">
        <div class="brand" aria-label="${t.common.brandTitle}">
          <span class="brand-copy">
            <strong>${t.common.brandTitle}</strong>
            <span>${t.common.brandSubtitle}</span>
          </span>
        </div>
        <nav class="nav" aria-label="Primary">
          <div class="nav-links">
            ${navItems.map(([key, label]) => `
              ${key === currentPage
                ? `<span class="nav-pill is-active" aria-current="page">${label}</span>`
                : `<a class="nav-pill" href="${pageUrl(key, lang)}">${label}</a>`
              }
            `).join("")}
          </div>
          <div class="lang-switch" aria-label="${t.common.langLabel}">
            ${LANGS.map((choice) => `
              <a class="lang-link${choice === lang ? " is-active" : ""}" href="${pageUrl(page, choice)}"${choice === lang ? ' aria-current="true"' : ""}>${choice.toUpperCase()}</a>
            `).join("")}
          </div>
        </nav>
      </div>
    </header>
  `;
}

function footer(t) {
  return `<footer class="footer"><div class="shell">${t.common.footer}</div></footer>`;
}

function list(items) {
  return `<ul>${items.map((item) => `<li>${item}</li>`).join("")}</ul>`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function formatTimestamp(value, lang) {
  if (!value) return "n/a";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return escapeHtml(value);
  return new Intl.DateTimeFormat(lang, {
    year: "numeric",
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit"
  }).format(date);
}

function formatMonth(value, lang) {
  if (!value || !/^\d{4}-\d{2}$/.test(value)) return escapeHtml(value || "");
  const date = new Date(`${value}-01T00:00:00Z`);
  return new Intl.DateTimeFormat(lang, {
    year: "numeric",
    month: "long"
  }).format(date);
}

function renderBreakdownList(rows, emptyLabel) {
  if (!Array.isArray(rows) || rows.length === 0) {
    return `<p>${emptyLabel}</p>`;
  }
  const max = Math.max(...rows.map((row) => Number(row.count || 0)), 1);
  return `
    <ul class="breakdown-list">
      ${rows.map((row) => {
        const count = Number(row.count || 0);
        const width = Math.max(8, Math.round((count / max) * 100));
        return `
          <li class="breakdown-row">
            <div class="breakdown-head">
              <span>${escapeHtml(row.label)}</span>
              <strong>${count}</strong>
            </div>
            <div class="breakdown-bar"><span style="width:${width}%"></span></div>
          </li>
        `;
      }).join("")}
    </ul>
  `;
}

function formatDurationHours(value, lang, t) {
  const hours = Number(value);
  if (!Number.isFinite(hours)) return t.statPage.noDurationData;
  if (hours >= 48) {
    return `${(hours / 24).toLocaleString(lang, { maximumFractionDigits: 1 })} ${t.statPage.daysUnit}`;
  }
  return `${hours.toLocaleString(lang, { maximumFractionDigits: 1 })} ${t.statPage.hoursUnit}`;
}

function statTemplate(lang, t, data) {
  const totals = data?.totals || {};
  const monthly = Array.isArray(data?.monthly) ? data.monthly : [];
  const breakdowns = data?.breakdowns || {};
  const durations = data?.durations || {};
  const manualConfigured = Boolean(data?.manual_stats_table?.configured);
  const monthlyColumnKeys = Object.keys(t.statPage.monthlyColumns);
  const introParagraphs = t.statPage.lede
    .split("\n\n")
    .map((paragraph) => `<p>${paragraph}</p>`)
    .join("");
  const totalCards = Object.entries(t.statPage.totals).map(([key, label]) => `
    <article class="stat-card kpi-card">
      <p>${label}</p>
      <strong>${Number(totals[key] || 0).toLocaleString(lang)}</strong>
    </article>
  `).join("");

  const breakdownPanels = Object.entries(t.statPage.breakdownLabels).map(([key, label]) => `
    <article class="panel breakdown-panel">
      <h3>${label}</h3>
      ${renderBreakdownList(breakdowns[key], t.statPage.emptyBreakdown)}
    </article>
  `).join("");

  const observationPanels = [
    {
      title: t.statPage.observationsCards.sectors,
      text: t.statPage.observationsTexts.sectors,
      content: renderBreakdownList(breakdowns.secteurs, t.statPage.emptyBreakdown)
    },
    {
      title: t.statPage.observationsCards.mobility,
      text: t.statPage.observationsTexts.mobility,
      content: renderBreakdownList(breakdowns.mobilite_candidats, t.statPage.emptyBreakdown)
    },
    {
      title: t.statPage.observationsCards.territories,
      text: t.statPage.observationsTexts.territories,
      content: renderBreakdownList(breakdowns.besoins_par_pays, t.statPage.emptyBreakdown)
    }
  ].map(({ title, text, content }) => `
    <article class="surface-card">
      <h3>${title}</h3>
      <p>${text}</p>
      ${content}
    </article>
  `).join("");

  const learningPanels = t.statPage.learnings.map(([title, text]) => `
    <article class="surface-card">
      <h3>${title}</h3>
      <p>${text}</p>
    </article>
  `).join("");

  const durationPanels = Object.entries(t.statPage.durationLabels).map(([key, label]) => {
    const row = durations[key] || {};
    return `
      <article class="panel breakdown-panel">
        <h3>${label}</h3>
        <ul class="breakdown-list">
          <li class="breakdown-row"><div class="breakdown-head"><span>${t.statPage.durationMetrics.count}</span><strong>${Number(row.count || 0).toLocaleString(lang)}</strong></div></li>
          <li class="breakdown-row"><div class="breakdown-head"><span>${t.statPage.durationMetrics.avg}</span><strong>${formatDurationHours(row.avg_hours, lang, t)}</strong></div></li>
          <li class="breakdown-row"><div class="breakdown-head"><span>${t.statPage.durationMetrics.median}</span><strong>${formatDurationHours(row.median_hours, lang, t)}</strong></div></li>
          <li class="breakdown-row"><div class="breakdown-head"><span>${t.statPage.durationMetrics.min}</span><strong>${formatDurationHours(row.min_hours, lang, t)}</strong></div></li>
          <li class="breakdown-row"><div class="breakdown-head"><span>${t.statPage.durationMetrics.max}</span><strong>${formatDurationHours(row.max_hours, lang, t)}</strong></div></li>
        </ul>
      </article>
    `;
  }).join("");

  return `
    ${nav("stat", lang, t)}
    <main id="main-content" tabindex="-1">
      <section class="hero">
        <div class="shell hero-grid">
          <article class="hero-card hero">
            <div class="eyebrow">${t.statPage.eyebrow}</div>
            <h1>${t.statPage.title}</h1>
            <div class="lede">${introParagraphs}</div>
            <div class="updated-card">
              <span class="updated-label">${t.statPage.updatedPrefix}</span>
              <strong>${formatTimestamp(data?.generated_at, lang)}</strong>
            </div>
            <div class="stat-meta">
              <div>${t.statPage.methodology}</div>
              <div>${manualConfigured ? t.statPage.manualNote : t.statPage.manualMissing}</div>
            </div>
          </article>
          <aside class="story-card">
            <h2>${t.statPage.keyFiguresTitle}</h2>
            <p>${t.statPage.keyFiguresLead}</p>
          </aside>
        </div>
      </section>

      <section class="section">
        <div class="shell">
          <div class="panel">
            <h2>${t.statPage.keyFiguresTitle}</h2>
            <p>${t.statPage.keyFiguresLead}</p>
          </div>
          <div class="stats-grid" style="margin-top: 1rem;">
            ${totalCards}
          </div>
        </div>
      </section>

      <section class="section">
        <div class="shell">
          <div class="panel">
            <h2>${t.statPage.observationsTitle}</h2>
            <p>${t.statPage.observationsLead}</p>
          </div>
          <div class="principles-grid" style="margin-top: 1rem;">
            ${observationPanels}
          </div>
        </div>
      </section>

      <section class="section">
        <div class="shell">
          <div class="panel"><h2>${t.statPage.learningsTitle}</h2></div>
          <div class="principles-grid" style="margin-top: 1rem;">
            ${learningPanels}
          </div>
        </div>
      </section>

      <section class="section">
        <div class="shell">
          <div class="panel">
            <h2>${t.statPage.detailedTitle}</h2>
            <p>${t.statPage.detailedLead}</p>
          </div>
        </div>
      </section>

      <section class="section">
        <div class="shell">
          <div class="panel">
            <h2>${t.statPage.monthlyTitle}</h2>
            <p>${t.statPage.monthlyLead}</p>
          </div>
          <div class="table-wrap">
            <table class="stats-table">
              <caption class="sr-only">${t.statPage.monthlyTitle}</caption>
              <thead>
                <tr>
                  ${Object.values(t.statPage.monthlyColumns).map((label) => `<th scope="col">${label}</th>`).join("")}
                </tr>
              </thead>
              <tbody>
                ${monthly.map((row) => `
                  <tr>
                    ${monthlyColumnKeys.map((key, index) => index === 0
                      ? `<th scope="row">${formatMonth(row[key], lang)}</th>`
                      : `<td>${Number(row[key] || 0).toLocaleString(lang)}</td>`).join("")}
                  </tr>
                `).join("")}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section class="section">
        <div class="shell">
          <div class="panel"><h2>${t.statPage.breakdownsTitle}</h2></div>
          <div class="dashboard-grid" style="margin-top: 1rem;">
            ${breakdownPanels}
          </div>
        </div>
      </section>

      <section class="section">
        <div class="shell">
          <details class="panel" open>
            <summary><span class="summary-title">${t.statPage.methodologyTitle}</span></summary>
            <div style="margin-top: 1rem;">
              <p>${t.statPage.methodology}</p>
              <p>${manualConfigured ? t.statPage.manualNote : t.statPage.manualMissing}</p>
              <div class="panel" style="margin-top: 1rem;"><h2>${t.statPage.durationsTitle}</h2></div>
              <div class="dashboard-grid" style="margin-top: 1rem;">
                ${durationPanels}
              </div>
            </div>
          </details>
        </div>
      </section>
    </main>
    ${footer(t)}
  `;
}

async function loadPublicStats() {
  const response = await fetch(`/api/forms/${FORM_ID}/public-stats`, {
    headers: { Accept: "application/json" }
  });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return response.json();
}

function homeTemplate(lang, t) {
  const storyParagraphs = t.home.storyText
    .split("\n\n")
    .map((paragraph) => `<p>${paragraph}</p>`)
    .join("");

  return `
    ${nav("home", lang, t)}
    <main id="main-content" tabindex="-1">
      <section class="hero">
        <div class="shell hero-grid">
          <article class="hero-card hero">
            <div class="eyebrow">${t.home.eyebrow}</div>
            <h1>${t.home.title}</h1>
            <p class="lede">${t.home.lede}</p>
            <div class="hero-actions">
              <a class="primary-action" href="${pageUrl("candidate-landing", lang)}">${t.common.ctaStartCandidate}</a>
              <a class="secondary-action" href="${pageUrl("employer-landing", lang)}">${t.common.ctaStartEmployer}</a>
            </div>
          </article>
          <aside class="story-card">
            <h2>${t.home.storyTitle}</h2>
            ${storyParagraphs}
          </aside>
        </div>
      </section>

      <section class="section" aria-labelledby="home-stats-title">
        <div class="shell stats-grid">
          <h2 id="home-stats-title" class="sr-only">${t.home.statsTitle}</h2>
          ${t.home.stats.map(([value, text]) => `
            <article class="stat-card">
              <strong>${value}</strong>
              <p>${text}</p>
            </article>
          `).join("")}
        </div>
      </section>

      <section class="section">
        <div class="shell">
          <div class="panel"><h2>${t.home.tracksTitle}</h2></div>
          <div class="tracks-grid" style="margin-top: 1rem;">
            <article class="surface-card">
              <h3>${t.home.candidateTitle}</h3>
              <p>${t.home.candidateText}</p>
              <div class="hero-actions">
                <a class="primary-action" href="${pageUrl("candidate-landing", lang)}">${t.common.ctaSeeCandidate}</a>
              </div>
            </article>
            <article class="surface-card">
              <h3>${t.home.employerTitle}</h3>
              <p>${t.home.employerText}</p>
              <div class="hero-actions">
                <a class="primary-action" href="${pageUrl("employer-landing", lang)}">${t.common.ctaSeeEmployer}</a>
              </div>
            </article>
          </div>
        </div>
      </section>

      <section class="section">
        <div class="shell">
          <div class="panel"><h2>${t.home.principlesTitle}</h2></div>
          <div class="principles-grid" style="margin-top: 1rem;">
            ${t.home.principles.map(([title, text]) => `
              <article class="surface-card">
                <h3>${title}</h3>
                <p>${text}</p>
              </article>
            `).join("")}
          </div>
        </div>
      </section>

      <section class="section">
        <div class="shell">
          <article class="panel">
            <h2>${t.home.perspectivesTitle}</h2>
            ${list(t.home.perspectivesBullets)}
          </article>
        </div>
      </section>
    </main>
    ${footer(t)}
  `;
}

function landingTemplate(page, lang, t, data) {
  const questionnairePage = page === "candidate-landing" ? "candidate-questionnaire" : "employer-questionnaire";
  if (page === "candidate-landing") {
    return `
      ${nav(page, lang, t)}
      <main id="main-content" class="section candidate-landing-page" tabindex="-1">
        <div class="shell candidate-landing-layout">
          <article class="candidate-letter">
            <div class="candidate-logos" role="group" aria-label="${t.common.partnersLabel}">
              <img src="${data.logos.eures.src}" alt="${data.logos.eures.alt}" class="logo-eures">
              <div class="candidate-badge">
                <img src="${data.logos.franceTravail.src}" alt="${data.logos.franceTravail.alt}" class="logo-france-travail">
                <span>France Travail</span>
              </div>
              <img src="${data.logos.europeanUnion.src}" alt="${data.logos.europeanUnion.alt}" class="logo-eu">
            </div>

            <div class="candidate-letter-head">
              <div class="kicker">${data.kicker}</div>
              <h1>${data.title}</h1>
              <p class="lede">${data.lede}</p>
            </div>

            <section class="candidate-message">
              <h2>${data.messageTitle}</h2>
              <p><strong>${data.messageIntro}</strong></p>
              ${data.messageBody.map((paragraph) => `<p>${paragraph}</p>`).join("")}
              <div class="candidate-highlight">${data.messageHighlight}</div>
              <div class="landing-actions">
                <a class="primary-action" href="${pageUrl(questionnairePage, lang)}">${t.common.ctaQuestionnaire}</a>
              </div>
            </section>

            <section class="candidate-about">
              <h2>${data.benefitsTitle || data.sideTitle}</h2>
              ${data.benefits ? list(data.benefits) : `<p>${data.sideText}</p>`}
            </section>
          </article>

          <aside class="candidate-sidebar">
            <article class="surface-card candidate-info-card">
              <h2>${data.bulletsTitle}</h2>
              ${data.bulletsLead ? `<p>${data.bulletsLead}</p>` : ""}
              ${list(data.bullets)}
              <ul class="tag-row" aria-label="${t.common.tagsLabel}">
                ${data.tags.map((tag) => `<li><span class="tag">${tag}</span></li>`).join("")}
              </ul>
            </article>

            <article class="surface-card candidate-info-card">
              <h2>${data.disclaimerTitle}</h2>
              ${data.processBullets ? list(data.processBullets) : ""}
              <p>${data.disclaimerText}</p>
            </article>

            <article class="panel candidate-info-card">
              <h2>${data.sideTitle}</h2>
              <p>${data.sideText}</p>
            </article>
          </aside>
        </div>
      </main>
      ${footer(t)}
    `;
  }

  return `
    ${nav(page, lang, t)}
    <main id="main-content" class="section" tabindex="-1">
      <div class="shell landing-grid">
        <article class="hero-card landing-card">
          <div class="kicker">${data.kicker}</div>
          <h1>${data.title}</h1>
          <p class="lede">${data.lede}</p>
          <ul class="tag-row" aria-label="${t.common.tagsLabel}">
            ${data.tags.map((tag) => `<li><span class="tag">${tag}</span></li>`).join("")}
          </ul>
          <div class="landing-actions">
            <a class="primary-action" href="${pageUrl(questionnairePage, lang)}">${t.common.ctaQuestionnaire}</a>
            <a class="secondary-action" href="${pageUrl("home", lang)}">${t.common.ctaBackHome}</a>
          </div>
        </article>
        <div class="landing-side">
          <article class="surface-card">
            <h2>${data.bulletsTitle}</h2>
            ${list(data.bullets)}
          </article>
          <article class="surface-card">
            <h2>${data.sideTitle}</h2>
            <p>${data.sideText}</p>
          </article>
        </div>
      </div>

      <div class="shell dashboard-grid" style="margin-top: 1rem;">
        <article class="panel">
          <h2>${t.common.matchingTitle}</h2>
          ${list(t.common.matchingBullets)}
        </article>
        <article class="panel">
          <h2>${t.common.futureTitle}</h2>
          ${list(t.common.futureBullets)}
        </article>
      </div>
    </main>
    ${footer(t)}
  `;
}

function choicePills(name, options) {
  return `
    <div class="choice-grid">
      ${options.map((option) => {
        const item = typeof option === "string" ? { value: option, label: option } : option;
        return `
        <label class="checkbox-pill">
          <input type="checkbox" name="${name}" value="${item.value}">
          <span>${item.label}</span>
        </label>
      `;
      }).join("")}
    </div>
  `;
}

function radioPills(name, options) {
  return `
    <div class="choice-grid">
      ${options.map((option) => {
        const item = typeof option === "string" ? { value: option, label: option } : option;
        return `
        <label class="checkbox-pill">
          <input type="radio" name="${name}" value="${item.value}" required>
          <span>${item.label}</span>
        </label>
      `;
      }).join("")}
    </div>
  `;
}

function matrixQuestion(title, rows, columns, hint = "", inputType = "checkbox", mobileHint = "") {
  const captionId = nextFieldErrorId();
  return `
    <fieldset class="fieldset matrix-question">
      <legend>${title}</legend>
      ${hint ? `<p class="mini-note">${hint}</p>` : ""}
      ${mobileHint ? `<p class="mini-note matrix-mobile-hint">${mobileHint}</p>` : ""}
      <div class="matrix-wrap">
        <table class="matrix-table" aria-describedby="${captionId}">
          <caption id="${captionId}" class="sr-only">${title}</caption>
          <thead>
            <tr>
              <th scope="col"><span class="sr-only">${title}</span></th>
              ${columns.map((column) => {
                const item = typeof column === "string" ? { value: column, label: column } : column;
                return `<th scope="col">${item.label}</th>`;
              }).join("")}
            </tr>
          </thead>
          <tbody>
            ${rows.map((row) => `
              <tr>
                <th scope="row">${row.label}</th>
                ${columns.map((column) => {
                  const item = typeof column === "string" ? { value: column, label: column } : column;
                  return `
                  <td data-column-label="${escapeHtml(item.label)}">
                    <label class="matrix-option">
                      <span class="matrix-option-label">${item.label}</span>
                      <input type="${inputType}" name="${row.field}" value="${item.value}" aria-label="${escapeHtml(`${title} - ${row.label} - ${item.label}`)}">
                    </label>
                  </td>
                `;
                }).join("")}
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    </fieldset>
  `;
}

function rankingQuestion(content) {
  return `
    <fieldset class="fieldset rank-question">
      <legend>${content.rankingTitle}</legend>
      <p class="mini-note">${content.rankingHint}</p>
      <div class="ranking-grid">
        ${content.rankingDisplayOptions.map((option, index) => `
          <div class="field rank-field">
            <label for="rank__tally_q17__${index}">${option}</label>
            <select id="rank__tally_q17__${index}" name="rank__tally_q17__${index}" required>
              <option value=""></option>
              ${content.rankingDisplayOptions.map((_, rankIndex) => `
                <option value="${rankIndex + 1}">${rankIndex + 1}</option>
              `).join("")}
            </select>
          </div>
        `).join("")}
      </div>
    </fieldset>
  `;
}

function salaryExpectationFields(baseName, content) {
  return `
    <div class="section-intro">
      <p class="mini-note">${content.salaryExpectationIntro}</p>
    </div>
    <div class="form-grid">
      <fieldset class="fieldset">
        <legend>${content.salaryFields.type}</legend>
        ${radioPills(`${baseName}_salary_type`, content.salaryUnits)}
      </fieldset>
      <label class="field">
        <span>${content.salaryFields.min}</span>
        <input type="number" name="${baseName}_salary_min" min="0" step="0.01" required>
      </label>
    </div>
  `;
}

function salaryOfferFields(baseName, content) {
  return `
    <div class="section-intro">
      <p class="mini-note">${content.salaryOfferIntro}</p>
    </div>
    <div class="form-grid">
      <fieldset class="fieldset">
        <legend>${content.salaryFields.type}</legend>
        ${radioPills(`${baseName}_salary_type`, content.salaryUnits)}
      </fieldset>
      <label class="field">
        <span>${content.salaryFields.min}</span>
        <input type="number" name="${baseName}_salary_min" min="0" step="0.01" required>
      </label>
      <label class="field">
        <span>${content.salaryFields.max}</span>
        <input type="number" name="${baseName}_salary_max" min="0" step="0.01" required>
      </label>
    </div>
  `;
}

function candidateTallyQuestionnaireTemplate(lang, t) {
  const logos = t.candidateLanding.logos;
  const content = getCandidateTallyContent(lang);
  return `
    ${nav("candidate-questionnaire", lang, t)}
    <main id="main-content" class="questionnaire-shell" tabindex="-1">
      <div class="shell questionnaire-grid">
        <section class="questionnaire-card candidate-letter questionnaire-letter">
          <div class="questionnaire-hero">
            <div class="candidate-logos">
              <img class="logo-eures" src="${logos.eures.src}" alt="${logos.eures.alt}">
              <div class="candidate-badge">
                <img class="logo-france-travail" src="${logos.franceTravail.src}" alt="${logos.franceTravail.alt}">
                <span>France Travail</span>
              </div>
              <img class="logo-eu" src="${logos.europeanUnion.src}" alt="${logos.europeanUnion.alt}">
            </div>
            <div class="eyebrow">${content.eyebrow}</div>
            <h1>${content.heroTitle}</h1>
            <p class="lede">${content.heroLede}</p>
            <div class="candidate-highlight">${content.heroHighlight}</div>
          </div>

          <form class="questionnaire-form" id="candidate-tally-form" data-role="candidate" novalidate>
            <section class="form-section">
              <h2>${content.overviewTitle}</h2>
              ${matrixQuestion(
                content.overviewMatrixTitle,
                content.countryRows,
                content.countryColumns,
                "",
                "checkbox",
                content.matrixMobileHint
              )}

              <fieldset class="fieldset">
                <legend>${content.mobilityTypeTitle}</legend>
                <p class="mini-note">${content.mobilityTypeHint}</p>
                ${choicePills("tally_q02", content.mobilityTypeOptions)}
              </fieldset>
            </section>

            <section class="form-section" data-condition="transfrontaliere">
              <h2>${content.crossBorderTitle}</h2>
              <fieldset class="fieldset">
                <legend>${content.questions.q03}</legend>
                ${radioPills("tally_q03", localizeOptions(["Oui", "Non"], content.options.yesNo))}
              </fieldset>
              <fieldset class="fieldset">
                <legend>${content.questions.q04}</legend>
                ${radioPills("tally_q04", localizeOptions(["30 min", "1h", "1h30", "2h", "Plus de 2h"], content.options.commute))}
              </fieldset>
              <fieldset class="fieldset">
                <legend>${content.questions.q05}</legend>
                ${choicePills("tally_q05", localizeOptions(["Voiture", "Train", "Bus", "Covoiturage", "Je ne sais pas encore"], content.options.transport))}
              </fieldset>
              <fieldset class="fieldset">
                <legend>${content.questions.q06}</legend>
                ${radioPills("tally_q06", localizeOptions(["Je suis disponible sur des horaires variés", "J’ai des contraintes ou préférences horaires"], content.options.schedule))}
              </fieldset>
              <div data-condition="horaire-precis">
                ${matrixQuestion(content.questions.q07, content.scheduleRows, content.scheduleColumns, "", "checkbox", content.matrixMobileHint)}
              </div>
              <fieldset class="fieldset">
                <legend>${content.questions.q08}</legend>
                ${choicePills("tally_q08", localizeOptions(["CDI", "CDD", "Intérim", "Saisonnier", "Temps plein", "Temps partiel"], content.options.contracts))}
              </fieldset>
              <fieldset class="fieldset">
                <legend>${content.questions.q09}</legend>
                ${radioPills("tally_q09", localizeOptions(["Dès que possible", "Dans les prochains jours", "Dans les prochaines semaines", "Dans 1 à 3 mois", "Je ne sais pas encore"], content.options.startDate))}
              </fieldset>
              ${matrixQuestion(
                content.questions.q10,
                content.documentsRows,
                content.documentsColumns,
                content.questions.q10Hint,
                "radio",
                content.matrixMobileHint
              )}
              <fieldset class="fieldset" data-condition="show-lu-social">
                <legend>${content.questions.q11}</legend>
                ${radioPills("tally_q11", localizeOptions(["Oui", "Non", "Je ne sais pas"], content.options.yesNoUnknown))}
              </fieldset>
              <fieldset class="fieldset" data-condition="show-de-social">
                <legend>${content.questions.q12}</legend>
                ${radioPills("raw_tally_q12", localizeOptions(["Oui", "Non", "Je ne sais pas"], content.options.yesNoUnknown))}
              </fieldset>
              <fieldset class="fieldset" data-condition="show-fr-social">
                <legend>${content.questions.q13}</legend>
                ${radioPills("raw_tally_q13", localizeOptions(["Oui", "Non", "Je ne sais pas"], content.options.yesNoUnknown))}
              </fieldset>
            </section>

            <section class="form-section" data-condition="expatriation">
              <h2>${content.expatriationTitle}</h2>
              <fieldset class="fieldset">
                <legend>${content.questions.q14}</legend>
                ${radioPills("tally_q14", localizeOptions(["Oui", "Non"], content.options.yesNo))}
              </fieldset>
              <fieldset class="fieldset">
                <legend>${content.questions.q15}</legend>
                ${radioPills("tally_q15", localizeOptions(["Dès que possible", "D'ici 3 mois", "Entre 3 et 6 mois", "Dans  plus de 6 mois", "Je ne sais pas"], content.options.departWhen))}
              </fieldset>
              <fieldset class="fieldset">
                <legend>${content.questions.q16}</legend>
                ${radioPills("tally_q16", localizeOptions(["Uniquement vous", "En couple", "En famille"], content.options.departWith))}
              </fieldset>
              ${rankingQuestion(content)}
            </section>

            <section class="form-section">
              <h2>${content.professionalTitle}</h2>
              ${matrixQuestion(content.questions.q18, content.languageRows, content.languageColumns, "", "radio", content.matrixMobileHint)}
              <fieldset class="fieldset">
                <legend>${content.questions.q19}</legend>
                ${choicePills("tally_q19", content.sectorsOptions)}
              </fieldset>
            </section>

            <section class="form-section" data-condition="sector-vente">
              <h3>${content.sectorTitles.vente}</h3>
              <fieldset class="fieldset">
                <legend>${content.sectorLegends.vente} <span class="mini-note">${content.questions.sectorHint}</span></legend>
                ${choicePills("tally_q20", localizeOptions(candidateTallyCopy.fr.sectorChoices.vente, content.sectorChoices.vente))}
              </fieldset>
              <fieldset class="fieldset">
                <legend>${content.questions.q21}</legend>
                ${radioPills("tally_q21", localizeOptions(["Oui, plus de 2 ans", "Oui, entre 6 mois et 2 ans", "Oui, moins de 6 mois", "Non, mais je suis intéressé(e) par le secteur"], content.options.experience))}
              </fieldset>
              ${salaryExpectationFields("tally_q20", content)}
            </section>

            <section class="form-section" data-condition="sector-nettoyage">
              <h3>${content.sectorTitles.nettoyage}</h3>
              <fieldset class="fieldset">
                <legend>${content.sectorLegends.nettoyage} <span class="mini-note">${content.questions.sectorHint}</span></legend>
                ${choicePills("tally_q22", localizeOptions(candidateTallyCopy.fr.sectorChoices.nettoyage, content.sectorChoices.nettoyage))}
              </fieldset>
              <fieldset class="fieldset">
                <legend>${content.questions.q23}</legend>
                ${radioPills("tally_q23", localizeOptions(["Oui, plus de 2 ans", "Oui, entre 6 mois et 2 ans", "Oui, moins de 6 mois", "Non, mais je suis intéressé(e) par le secteur"], content.options.experience))}
              </fieldset>
              <fieldset class="fieldset">
                <legend>${content.questions.q24}</legend>
                ${radioPills("tally_q24", localizeOptions(["Oui", "Non", "Je peux en faire la demande rapidement", "Je ne sais pas"], content.options.backgroundCheck))}
              </fieldset>
              ${salaryExpectationFields("tally_q22", content)}
            </section>

            <section class="form-section" data-condition="sector-hotel">
              <h3>${content.sectorTitles.hotel}</h3>
              <fieldset class="fieldset">
                <legend>${content.sectorLegends.hotel} <span class="mini-note">${content.questions.sectorHint}</span></legend>
                ${choicePills("tally_q25", localizeOptions(candidateTallyCopy.fr.sectorChoices.hotel, content.sectorChoices.hotel))}
              </fieldset>
              <fieldset class="fieldset">
                <legend>${content.questions.q26}</legend>
                ${radioPills("tally_q26", localizeOptions(["Oui, plus de 2 ans", "Oui, entre 6 mois et 2 ans", "Oui, moins de 6 mois", "Non, mais je suis intéressé(e) par le secteur"], content.options.experience))}
              </fieldset>
              ${salaryExpectationFields("tally_q25", content)}
            </section>

            <section class="form-section" data-condition="sector-agri">
              <h3>${content.sectorTitles.agri}</h3>
              <fieldset class="fieldset">
                <legend>${content.sectorLegends.agri} <span class="mini-note">${content.questions.sectorHint}</span></legend>
                ${choicePills("tally_q27", localizeOptions(candidateTallyCopy.fr.sectorChoices.agri, content.sectorChoices.agri))}
              </fieldset>
              <fieldset class="fieldset">
                <legend>${content.questions.q28}</legend>
                ${radioPills("tally_q28", localizeOptions(["Oui, plus de 2 ans", "Oui, entre 6 mois et 2 ans", "Oui, moins de 6 mois", "Non, mais je suis intéressé(e) par le secteur"], content.options.experience))}
              </fieldset>
              ${salaryExpectationFields("tally_q27", content)}
            </section>

            <section class="form-section" data-condition="sector-polyvalent">
              <h3>${content.sectorTitles.polyvalent}</h3>
              <fieldset class="fieldset">
                <legend>${content.sectorLegends.polyvalent} <span class="mini-note">${content.questions.sectorHint}</span></legend>
                ${choicePills("tally_q29", localizeOptions(candidateTallyCopy.fr.sectorChoices.polyvalent, content.sectorChoices.polyvalent))}
              </fieldset>
              <fieldset class="fieldset">
                <legend>${content.questions.q30}</legend>
                ${radioPills("tally_q30", localizeOptions(["Oui, plus de 2 ans", "Oui, entre 6 mois et 2 ans", "Oui, moins de 6 mois", "Non, mais je suis intéressé(e) par le secteur"], content.options.experience))}
              </fieldset>
              ${salaryExpectationFields("tally_q29", content)}
            </section>

            <section class="form-section">
              <h2>${content.contactTitle}</h2>
              <div class="form-grid">
                <label class="field">
                  <span>${content.questions.firstName}</span>
                  <input type="text" name="tally_q31" autocomplete="given-name" required>
                </label>
                <label class="field">
                  <span>${content.questions.lastName}</span>
                  <input type="text" name="tally_q32" autocomplete="family-name" required>
                </label>
                <label class="field">
                  <span>${content.questions.email}</span>
                  <input type="email" name="tally_q33" autocomplete="email" inputmode="email" required>
                </label>
                <label class="field">
                  <span>${content.questions.phone}</span>
                  <input type="tel" name="tally_q34" autocomplete="tel" inputmode="tel" required>
                </label>
              </div>
              <label class="field">
                <span>${content.questions.city}</span>
                <input type="text" name="tally_q35" autocomplete="address-level2" required>
              </label>
              <label class="field">
                <span>${content.questions.cv}</span>
                <input type="file" name="file__tally_q36" accept=".pdf,.doc,.docx,.odt">
                <p class="mini-note">${content.fileNote}</p>
              </label>
            </section>

            <section class="form-section">
              <label class="checkbox-pill consent-pill">
                <input type="checkbox" name="tally_q37" value="yes" required>
                <span>${content.consentText}</span>
              </label>
            </section>

            <div class="questionnaire-actions">
              <button class="primary-action" type="submit" id="save-btn">${t.common.submit}</button>
              <a class="ghost-action" href="${pageUrl("candidate-landing", lang)}">${t.common.ctaBackHome}</a>
            </div>
            <div class="status" id="status" role="status" aria-live="polite"></div>
          </form>
        </section>

        <aside class="candidate-sidebar">
          <section class="questionnaire-card candidate-info-card">
            <h2>${content.sidebarWhyTitle}</h2>
            <p>${content.sidebarWhyText}</p>
          </section>
          <section class="questionnaire-card candidate-info-card">
            <h2>${content.sidebarAfterTitle}</h2>
            <p>${content.sidebarAfterText}</p>
          </section>
          <section class="questionnaire-card candidate-info-card">
            <h2>${content.sidebarResumeTitle}</h2>
            <p class="mini-note">${content.sidebarResumeText}</p>
            <div class="uuid-box" id="uuid-box"></div>
          </section>
        </aside>
      </div>
    </main>
    ${footer(t)}
  `;
}

function employerLandingTemplate(lang, t) {
  const data = t.employerLanding;
  const logos = t.candidateLanding.logos;
  return `
    ${nav("employer-landing", lang, t)}
    <main id="main-content" class="section candidate-landing-page" tabindex="-1">
      <div class="shell candidate-landing-layout">
        <article class="candidate-letter">
          <div class="candidate-logos" role="group" aria-label="${t.common.partnersLabel}">
            <img src="${logos.eures.src}" alt="${logos.eures.alt}" class="logo-eures">
            <div class="candidate-badge">
              <img src="${logos.franceTravail.src}" alt="${logos.franceTravail.alt}" class="logo-france-travail">
              <span>France Travail</span>
            </div>
            <img src="${logos.europeanUnion.src}" alt="${logos.europeanUnion.alt}" class="logo-eu">
          </div>

          <div class="candidate-letter-head">
            <div class="kicker">${data.kicker}</div>
            <h1>${data.title}</h1>
            <p class="lede">${data.lede}</p>
          </div>

          <section class="candidate-message">
            <h2>${data.messageTitle || data.bulletsTitle}</h2>
            <p><strong>${data.messageIntro || data.sideText}</strong></p>
            ${(data.messageBody || []).map((paragraph) => `<p>${paragraph}</p>`).join("")}
            ${data.messageHighlight ? `<div class="candidate-highlight">${data.messageHighlight}</div>` : ""}
            <div class="landing-actions">
              <a class="primary-action" href="${pageUrl("employer-questionnaire", lang)}">${t.common.ctaQuestionnaire}</a>
            </div>
            ${data.messageOutcome ? `<p>${data.messageOutcome}</p>` : ""}
            ${data.signatureTitle ? `<p><strong>${data.signatureTitle}</strong><br>${data.signatureName}<br>${data.signatureRole}</p>` : ""}
          </section>

          <section class="candidate-about">
            <h2>${data.benefitsTitle || data.sideTitle}</h2>
            ${data.benefits ? list(data.benefits) : `<p>${data.sideText}</p>`}
          </section>
        </article>

        <aside class="candidate-sidebar">
          <article class="surface-card candidate-info-card">
            <h2>${data.bulletsTitle}</h2>
            ${data.bulletsLead ? `<p>${data.bulletsLead}</p>` : ""}
            ${list(data.bullets)}
            <ul class="tag-row" aria-label="${t.common.tagsLabel}">
              ${data.tags.map((tag) => `<li><span class="tag">${tag}</span></li>`).join("")}
            </ul>
          </article>

          <article class="surface-card candidate-info-card">
            <h2>${data.disclaimerTitle || t.common.futureTitle}</h2>
            ${data.processBullets ? list(data.processBullets) : ""}
            <p>${data.disclaimerText || data.sideText}</p>
          </article>

          <article class="panel candidate-info-card">
            <h2>${data.sideTitle}</h2>
            <p>${data.sideText}</p>
          </article>
        </aside>
      </div>
    </main>
    ${footer(t)}
  `;
}

function employerTallyQuestionnaireTemplate(lang, t) {
  const logos = t.candidateLanding.logos;
  const content = getEmployerTallyContent(lang);
  return `
    ${nav("employer-questionnaire", lang, t)}
    <main id="main-content" class="questionnaire-shell" tabindex="-1">
      <div class="shell questionnaire-grid">
        <section class="questionnaire-card candidate-letter questionnaire-letter">
          <div class="questionnaire-hero">
            <div class="candidate-logos">
              <img class="logo-eures" src="${logos.eures.src}" alt="${logos.eures.alt}">
              <div class="candidate-badge">
                <img class="logo-france-travail" src="${logos.franceTravail.src}" alt="${logos.franceTravail.alt}">
                <span>France Travail</span>
              </div>
              <img class="logo-eu" src="${logos.europeanUnion.src}" alt="${logos.europeanUnion.alt}">
            </div>
            <div class="eyebrow">${content.eyebrow}</div>
            <h1>${content.heroTitle}</h1>
            <p class="lede">${content.heroLede}</p>
            <div class="candidate-highlight">${content.heroHighlight}</div>
          </div>

          <form class="questionnaire-form" id="employer-tally-form" data-role="employer" novalidate>
            <section class="form-section">
              <h2>${content.sections.need}</h2>
              <div class="section-intro">
                <p class="mini-note">${content.introNote}</p>
                <p class="mini-note">${content.introNote2}</p>
              </div>
              <fieldset class="fieldset">
                <legend>${content.questions.q01}</legend>
                ${choicePills("tally_q01", content.sectorsOptions)}
              </fieldset>
              ${matrixQuestion(content.questions.q02, content.languageRows, content.languageColumns, content.questions.q02Hint, "radio", content.matrixMobileHint)}
              <fieldset class="fieldset">
                <legend>${content.questions.q03}</legend>
                ${radioPills("tally_q03", content.optionGroups.q03)}
              </fieldset>
              <fieldset class="fieldset">
                <legend>${content.questions.q04}</legend>
                ${radioPills("tally_q04", content.optionGroups.q04)}
              </fieldset>
              <label class="field">
                <span>${content.questions.q20}</span>
                <input type="text" name="tally_q20" required>
              </label>
              <fieldset class="fieldset">
                <legend>${content.questions.q05}</legend>
                ${choicePills("tally_q05", content.optionGroups.q05)}
              </fieldset>
              <fieldset class="fieldset">
                <legend>${content.questions.q06}</legend>
                ${choicePills("tally_q06", content.optionGroups.q06)}
              </fieldset>
            </section>

            <section class="form-section">
              <h2>${content.sections.conditions}</h2>
              <div class="section-intro">
                <p class="mini-note">Décrivez ici les profils que vous pouvez accueillir, les aides éventuelles à l’arrivée et les critères qui comptent vraiment pour vous.</p>
              </div>
              <fieldset class="fieldset">
                <legend>${content.questions.q07}</legend>
                ${choicePills("tally_q07", content.optionGroups.q07)}
              </fieldset>
              <fieldset class="fieldset">
                <legend>${content.questions.q08}</legend>
                ${choicePills("tally_q08", content.optionGroups.q08)}
              </fieldset>
              <fieldset class="fieldset">
                <legend>${content.questions.q09}</legend>
                ${choicePills("tally_q09", content.optionGroups.q09)}
              </fieldset>
            </section>

            ${["tally_q10", "tally_q11", "tally_q12", "tally_q13", "tally_q14"].map((name, index) => `
              <section class="form-section" data-condition="employer-sector-${index}">
                <h3>${content.sectorTitles[name]}</h3>
                <fieldset class="fieldset">
                  <legend>${index === 4 ? content.questions.q14 : content.questions[`q${10 + index}`]} <span class="mini-note">${content.questions.q14Hint}</span></legend>
                  ${choicePills(name, content.sectorPriorityOptions[name])}
                </fieldset>
                ${salaryOfferFields(name, content)}
              </section>
            `).join("")}

            <section class="form-section">
              <div class="field">
                <label for="tally_q20_extra">${content.questions.q20Extra}</label>
                <textarea id="tally_q20_extra" name="tally_q20_extra" rows="3"></textarea>
              </div>
            </section>

            <section class="form-section">
              <fieldset class="fieldset">
                <legend>${content.questions.q15}</legend>
                ${choicePills("tally_q15", content.optionGroups.q15)}
              </fieldset>
            </section>

            <section class="form-section">
              <h2>${content.sections.contact}</h2>
              <div class="section-intro">
                <p class="mini-note">Ces informations nous permettent de vous recontacter rapidement si des profils semblent compatibles avec votre besoin.</p>
              </div>
              <div class="form-grid">
                <label class="field">
                  <span>${content.questions.q16}</span>
                  <input type="text" name="tally_q16" autocomplete="name" required>
                </label>
                <label class="field">
                  <span>${content.questions.q17}</span>
                  <input type="text" name="tally_q17" autocomplete="organization" required>
                </label>
                <label class="field">
                  <span>${content.questions.q18}</span>
                  <input type="email" name="tally_q18" autocomplete="email" inputmode="email" required>
                </label>
                <label class="field">
                  <span>${content.questions.q19}</span>
                  <input type="tel" name="tally_q19" autocomplete="tel" inputmode="tel" required>
                </label>
              </div>
            </section>

            <section class="form-section">
              <h2>${content.questions.q21Title}</h2>
              <p class="mini-note">${content.questions.q21Text}</p>
              <p class="mini-note">${content.questions.q21Text2}</p>
              <p class="mini-note"><strong>${content.questions.q21Text3}</strong></p>
              <label class="checkbox-pill consent-pill">
                <input type="checkbox" name="tally_q21" value="yes" required>
                <span>${content.questions.consent}</span>
              </label>
            </section>

            <div class="questionnaire-actions">
              <button class="primary-action" type="submit" id="save-btn">${t.common.submit}</button>
              <a class="ghost-action" href="${pageUrl("employer-landing", lang)}">${t.common.ctaBackHome}</a>
            </div>
            <div class="status" id="status" role="status" aria-live="polite"></div>
          </form>
        </section>

        <aside class="candidate-sidebar">
          <section class="questionnaire-card candidate-info-card">
            <h2>${content.sidebarWhyTitle}</h2>
            <p>${content.sidebarWhyText}</p>
          </section>
          <section class="questionnaire-card candidate-info-card">
            <h2>${content.sidebarAfterTitle}</h2>
            <p>${content.sidebarAfterText}</p>
          </section>
          <section class="questionnaire-card candidate-info-card">
            <h2>${content.sidebarResumeTitle}</h2>
            <p class="mini-note">${content.sidebarResumeText}</p>
            <div class="uuid-box" id="uuid-box"></div>
          </section>
        </aside>
      </div>
    </main>
    ${footer(t)}
  `;
}

function isCheckedValue(form, name, value) {
  return Array.from(form.querySelectorAll(`input[name="${name}"]`)).some((input) => input.checked && input.value === value);
}

function toggleConditionBlocks(form) {
  const transfrontaliere = isCheckedValue(form, "tally_q02", "Transfrontalière");
  const expatriation = isCheckedValue(form, "tally_q02", "Expatriation");
  const horairePrecis = (form.querySelector('input[name="tally_q06"]:checked') || {}).value === "J’ai des contraintes ou préférences horaires";

  const q01lu = Array.from(form.querySelectorAll('input[name="tally_q01_f03"]:checked')).map((input) => input.value);
  const q01de = Array.from(form.querySelectorAll('input[name="tally_q01_f01"]:checked')).map((input) => input.value);
  const q01fr = Array.from(form.querySelectorAll('input[name="tally_q01_f02"]:checked')).map((input) => input.value);
  const selectedSectors = Array.from(form.querySelectorAll('input[name="tally_q19"]:checked')).map((input) => input.value);

  const visibility = {
    transfrontaliere,
    expatriation,
    "horaire-precis": horairePrecis,
    "show-lu-social": q01lu.includes("Je veux y travailler") && !q01lu.includes("J'y habite"),
    "show-de-social": q01de.includes("Je veux y travailler") && !q01de.includes("J'y habite"),
    "show-fr-social": q01fr.includes("Je veux y travailler") && !q01fr.includes("J'y habite"),
    "sector-vente": selectedSectors.includes(candidateTallyMeta.sectors[0]),
    "sector-nettoyage": selectedSectors.includes(candidateTallyMeta.sectors[1]),
    "sector-hotel": selectedSectors.includes(candidateTallyMeta.sectors[2]),
    "sector-agri": selectedSectors.includes(candidateTallyMeta.sectors[3]),
    "sector-polyvalent": selectedSectors.includes(candidateTallyMeta.sectors[4])
  };

  function shouldShow(element) {
    let current = element;
    while (current && current !== form) {
      if (current.dataset && current.dataset.condition && !visibility[current.dataset.condition]) {
        return false;
      }
      current = current.parentElement;
    }
    return true;
  }

  form.querySelectorAll("[data-condition]").forEach((element) => {
    const shown = shouldShow(element);
    element.hidden = !shown;
    element.setAttribute("aria-hidden", shown ? "false" : "true");
    element.querySelectorAll("input, select, textarea, button").forEach((control) => {
      if (control.id === "save-btn" || control.type === "hidden") {
        return;
      }
      control.disabled = !shown;
    });
  });
}

function humanizeCandidateRawAnswers(fields, fileMeta, rankingSummary) {
  return {
    pays_mobilite: {
      allemagne: fields.tally_q01_f01 || [],
      france: fields.tally_q01_f02 || [],
      luxembourg: fields.tally_q01_f03 || [],
      autre_pays_ue: fields.tally_q01_f04 || [],
      autre_pays_hors_ue: fields.tally_q01_f05 || []
    },
    type_mobilite: fields.tally_q02 || [],
    frontalier: {
      deja_travaille: fields.tally_q03 || "",
      trajet_max: fields.tally_q04 || "",
      transport: fields.tally_q05 || [],
      disponibilites_horaires: fields.tally_q06 || "",
      grille_horaire: {
        lundi: fields.tally_q07_f01 || [],
        mardi: fields.tally_q07_f02 || [],
        mercredi: fields.tally_q07_f03 || [],
        jeudi: fields.tally_q07_f04 || [],
        vendredi: fields.tally_q07_f05 || [],
        samedi: fields.tally_q07_f06 || [],
        dimanche: fields.tally_q07_f07 || []
      },
      contrats: fields.tally_q08 || [],
      dispo_demarrage: fields.tally_q09 || "",
      documents: {
        identite: fields.tally_q10_f01 || [],
        cv: fields.tally_q10_f02 || [],
        diplomes: fields.tally_q10_f03 || [],
        iban: fields.tally_q10_f04 || [],
        securite_sociale: fields.tally_q10_f05 || []
      },
      secu_lux: fields.tally_q11 || "",
      secu_de: fields.raw_tally_q12 || "",
      secu_fr: fields.raw_tally_q13 || ""
    },
    expatriation: {
      deja_vécu_etranger: fields.tally_q14 || "",
      quand_partir: fields.tally_q15 || "",
      partir_avec: fields.tally_q16 || "",
      priorites: rankingSummary
    },
    langues: {
      allemand: fields.tally_q18_f01 || [],
      anglais: fields.tally_q18_f02 || [],
      francais: fields.tally_q18_f03 || [],
      luxembourgeois: fields.tally_q18_f04 || []
    },
    secteurs: fields.tally_q19 || [],
    vente: {
      qualites: fields.tally_q20 || [],
      experience: fields.tally_q21 || "",
      salaire: { type: fields.tally_q20_salary_type || "", minimum: fields.tally_q20_salary_min || "", note: fields.tally_q20_salary_note || "" }
    },
    nettoyage: {
      qualites: fields.tally_q22 || [],
      experience: fields.tally_q23 || "",
      casier: fields.tally_q24 || "",
      salaire: { type: fields.tally_q22_salary_type || "", minimum: fields.tally_q22_salary_min || "", note: fields.tally_q22_salary_note || "" }
    },
    hotel_restaurant: {
      qualites: fields.tally_q25 || [],
      experience: fields.tally_q26 || "",
      salaire: { type: fields.tally_q25_salary_type || "", minimum: fields.tally_q25_salary_min || "", note: fields.tally_q25_salary_note || "" }
    },
    agriculture: {
      qualites: fields.tally_q27 || [],
      experience: fields.tally_q28 || "",
      salaire: { type: fields.tally_q27_salary_type || "", minimum: fields.tally_q27_salary_min || "", note: fields.tally_q27_salary_note || "" }
    },
    missions_polyvalentes: {
      qualites: fields.tally_q29 || [],
      experience: fields.tally_q30 || "",
      salaire: { type: fields.tally_q29_salary_type || "", minimum: fields.tally_q29_salary_min || "", note: fields.tally_q29_salary_note || "" }
    },
    contact: {
      prenom: fields.tally_q31 || "",
      nom: fields.tally_q32 || "",
      email: fields.tally_q33 || "",
      telephone: fields.tally_q34 || "",
      ville: fields.tally_q35 || ""
    },
    cv: fileMeta,
    consentement_rgpd: fields.tally_q37 || ""
  };
}

function enforceCheckboxLimit(form, groupNames, max, setStatus, message, changedInput = null) {
  groupNames.forEach((name) => {
    const inputs = Array.from(form.querySelectorAll(`input[type="checkbox"][name="${name}"]`))
      .filter((input) => !input.disabled || input.checked);

    if (!inputs.length) {
      return;
    }

    const checkedCount = inputs.filter((input) => input.checked).length;
    if (changedInput && changedInput.name === name && changedInput.checked && checkedCount > max) {
      changedInput.checked = false;
      setStatus(message, "error");
      const container = changedInput.closest(".fieldset") || changedInput.closest(".form-section");
      if (container) {
        let note = container.querySelector(".limit-note");
        if (!note) {
          note = document.createElement("p");
          note.className = "limit-note";
          container.appendChild(note);
        }
        note.textContent = message;
      }
    }

    const finalCheckedCount = inputs.filter((input) => input.checked).length;
    const limitReached = finalCheckedCount >= max;
    const container = inputs[0].closest(".fieldset") || inputs[0].closest(".form-section");
    const note = container ? container.querySelector(".limit-note") : null;
    if (note && finalCheckedCount < max) {
      note.remove();
    }
    inputs.forEach((input) => {
      if (input.checked) {
        return;
      }
      input.disabled = limitReached;
    });
  });
}

function toggleEmployerConditionBlocks(form) {
  const selectedSectors = Array.from(form.querySelectorAll('input[name="tally_q01"]:checked')).map((input) => input.value);
  const visibility = {
    "employer-sector-0": selectedSectors.includes(employerTallyMeta.sectors[0]),
    "employer-sector-1": selectedSectors.includes(employerTallyMeta.sectors[1]),
    "employer-sector-2": selectedSectors.includes(employerTallyMeta.sectors[2]),
    "employer-sector-3": selectedSectors.includes(employerTallyMeta.sectors[3]),
    "employer-sector-4": selectedSectors.includes(employerTallyMeta.sectors[4])
  };

  form.querySelectorAll("[data-condition]").forEach((element) => {
    const shown = Boolean(visibility[element.dataset.condition]);
    element.hidden = !shown;
    element.setAttribute("aria-hidden", shown ? "false" : "true");
    element.querySelectorAll("input, select, textarea, button").forEach((control) => {
      if (control.id === "save-btn" || control.type === "hidden") {
        return;
      }
      control.disabled = !shown;
    });
  });
}

function humanizeEmployerRawAnswers(fields) {
  return {
    secteur: fields.tally_q01 || [],
    langues: {
      allemand: fields.tally_q02_f01 || [],
      anglais: fields.tally_q02_f02 || [],
      francais: fields.tally_q02_f03 || [],
      luxembourgeois: fields.tally_q02_f04 || []
    },
    volume_recrutement: fields.tally_q03 || "",
    date_besoin: fields.tally_q04 || "",
    duree_contrat: fields.tally_q05 || [],
    volume_hebdomadaire: fields.tally_q06 || [],
    profils_acceptes: fields.tally_q07 || [],
    aides_installation: fields.tally_q08 || [],
    indispensables: fields.tally_q09 || [],
    priorites_vente: {
      choix: fields.tally_q10 || [],
      salaire: { type: fields.tally_q10_salary_type || "", minimum: fields.tally_q10_salary_min || "", maximum: fields.tally_q10_salary_max || "", note: fields.tally_q10_salary_note || "" }
    },
    priorites_nettoyage: {
      choix: fields.tally_q11 || [],
      salaire: { type: fields.tally_q11_salary_type || "", minimum: fields.tally_q11_salary_min || "", maximum: fields.tally_q11_salary_max || "", note: fields.tally_q11_salary_note || "" }
    },
    priorites_hotel: {
      choix: fields.tally_q12 || [],
      salaire: { type: fields.tally_q12_salary_type || "", minimum: fields.tally_q12_salary_min || "", maximum: fields.tally_q12_salary_max || "", note: fields.tally_q12_salary_note || "" }
    },
    priorites_agriculture: {
      choix: fields.tally_q13 || [],
      salaire: { type: fields.tally_q13_salary_type || "", minimum: fields.tally_q13_salary_min || "", maximum: fields.tally_q13_salary_max || "", note: fields.tally_q13_salary_note || "" }
    },
    priorites_polyvalent: {
      choix: fields.tally_q14 || [],
      salaire: { type: fields.tally_q14_salary_type || "", minimum: fields.tally_q14_salary_min || "", maximum: fields.tally_q14_salary_max || "", note: fields.tally_q14_salary_note || "" }
    },
    conditions_travail: fields.tally_q15 || [],
    contact: {
      prenom: fields.tally_q16 || "",
      entreprise: fields.tally_q17 || "",
      email: fields.tally_q18 || "",
      telephone: fields.tally_q19 || "",
      lieux_travail: fields.tally_q20 || "",
      autres_metiers_souhaites: fields.tally_q20_extra || ""
    },
    consentement_rgpd: fields.tally_q21 || ""
  };
}

function attachEmployerTallyBehavior(lang, t) {
  const form = document.getElementById("employer-tally-form");
  if (!form) {
    return;
  }
  const content = getEmployerTallyContent(lang);
  const inviteToken = currentInviteToken();
  const uuid = getUuid("employer");
  const statusEl = document.getElementById("status");
  const uuidBox = document.getElementById("uuid-box");
  const saveBtn = document.getElementById("save-btn");
  uuidBox.textContent = `${t.common.uuidPrefix}: ${uuid}`;

  function setStatus(message, state = "") {
    setStatusMessage(statusEl, message, state);
  }

  const limitedGroups = ["tally_q10", "tally_q11", "tally_q12", "tally_q13", "tally_q14"];

  function collectValues() {
    const data = new FormData(form);
    const values = {};
    for (const [key, rawValue] of data.entries()) {
      const value = String(rawValue || "").trim();
      if (!value) {
        continue;
      }
      if (values[key]) {
        if (Array.isArray(values[key])) {
          values[key].push(value);
        } else {
          values[key] = [values[key], value];
        }
      } else {
        values[key] = value;
      }
    }
    return values;
  }

  function validateCheckboxGroup(name, label, min = 1, max = Infinity) {
    if (!validateVisibleCheckboxGroup(form, name, label, setStatus, t, min, max)) {
      if (min === 1 && max === Infinity) {
        setStatus(`${content.errors.chooseAtLeastOne} ${label}. ${t.common.validation.checkHighlighted}`, "error");
      } else if (max !== Infinity) {
        setStatus(`${content.errors.chooseBetween} ${label}. ${t.common.validation.checkHighlighted}`, "error");
      }
      return false;
    }
    return true;
  }

  form.addEventListener("change", () => toggleEmployerConditionBlocks(form));
  form.addEventListener("input", () => toggleEmployerConditionBlocks(form));
  form.addEventListener("change", (event) => {
    clearFieldErrorState(event.target);
  });
  form.addEventListener("input", (event) => {
    clearFieldErrorState(event.target);
  });
  toggleEmployerConditionBlocks(form);
  enforceCheckboxLimit(form, limitedGroups, 4, setStatus, content.errors.maxFour);

  form.addEventListener("change", (event) => {
    toggleEmployerConditionBlocks(form);
    enforceCheckboxLimit(form, limitedGroups, 4, setStatus, content.errors.maxFour, event.target);
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (showFirstInvalidControl(form, setStatus, t)) {
      return;
    }

    const validations = [
      ["tally_q01", content.questions.q01],
      ...employerTallyMeta.languageRows.map((row) => [row.field, `${content.questions.q02} - ${row.label}`, 1, 1]),
      ["tally_q05", content.questions.q05],
      ["tally_q06", content.questions.q06],
      ["tally_q07", content.questions.q07],
      ["tally_q08", content.questions.q08],
      ["tally_q09", content.questions.q09],
      ["tally_q10", content.questions.q10, 1, 4],
      ["tally_q11", content.questions.q11, 1, 4],
      ["tally_q12", content.questions.q12, 1, 4],
      ["tally_q13", content.questions.q13, 1, 4],
      ["tally_q14", content.questions.q14, 1, 4],
      ["tally_q15", content.questions.q15]
    ];
    for (const [name, label, min, max] of validations) {
      if (!validateCheckboxGroup(name, label, min, max)) {
        return;
      }
    }

    const normalized = collectValues();
    const rawAnswers = humanizeEmployerRawAnswers(normalized);
    const languageSummary = employerTallyMeta.languageRows
      .map((row) => `${row.label}: ${Array.isArray(normalized[row.field]) ? normalized[row.field].join(", ") : ""}`)
      .filter((line) => !line.endsWith(": "));
    const prioritySummary = [
      normalized.tally_q09 || [],
      normalized.tally_q10 || [],
      normalized.tally_q11 || [],
      normalized.tally_q12 || [],
      normalized.tally_q13 || [],
      normalized.tally_q14 || []
    ].flat();

    const fields = {
      id_tally: uuid,
      tally_form_id: employerTallyMeta.formId,
      tally_respondent_id: uuid,
      tally_submitted_at: new Date().toISOString(),
      tally_raw_json: JSON.stringify(rawAnswers),
      employeur: normalized.tally_q17 || "",
      contact: normalized.tally_q16 || "",
      pays: normalized.tally_q20 || "",
      poste: Array.isArray(normalized.tally_q01) ? normalized.tally_q01.join(" | ") : (normalized.tally_q01 || ""),
      competences_requises: prioritySummary.join(" | "),
      langues_requises: languageSummary.join(" | "),
      date_debut: normalized.tally_q04 || "",
      pays_normalise: normalized.tally_q20 || "",
      lieu_travail_normalise: normalized.tally_q20 || "",
      competences_clefs: Array.isArray(normalized.tally_q09) ? normalized.tally_q09.join(" | ") : (normalized.tally_q09 || ""),
      contraintes_travail: Array.isArray(normalized.tally_q15) ? normalized.tally_q15.join(" | ") : (normalized.tally_q15 || ""),
      profils_acceptes: Array.isArray(normalized.tally_q07) ? normalized.tally_q07.join(" | ") : (normalized.tally_q07 || ""),
      aides_installation: Array.isArray(normalized.tally_q08) ? normalized.tally_q08.join(" | ") : (normalized.tally_q08 || ""),
      flow_role: "employer",
      ui_language: lang,
      source_page: "employer-questionnaire",
      form_version: "2026-06-tally-employer-v1",
      ...Object.fromEntries(
        Object.entries(normalized).map(([key, value]) => [
          key,
          Array.isArray(value) ? value.join(" | ") : value
        ])
      )
    };
    if (inviteToken) {
      fields.invite_token = inviteToken;
    }

    saveBtn.disabled = true;
    setStatus(t.common.saving);

    try {
      const response = await fetch(`/api/forms/${FORM_ID}/record`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: JSON.stringify({ fields })
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(payload.error || `${t.common.saveErrorPrefix} (${response.status})`);
      }
      setStatus(t.common.saved, "success");
    } catch (error) {
      const message = error && error.message ? error.message : t.common.saveErrorPrefix;
      setStatus(`${t.common.saveErrorPrefix}: ${message}`, "error");
    } finally {
      saveBtn.disabled = false;
    }
  });
}

function attachCandidateTallyBehavior(lang, t) {
  const form = document.getElementById("candidate-tally-form");
  if (!form) {
    return;
  }
  const content = getCandidateTallyContent(lang);
  const inviteToken = currentInviteToken();

  const uuid = getUuid("candidate");
  const statusEl = document.getElementById("status");
  const uuidBox = document.getElementById("uuid-box");
  const saveBtn = document.getElementById("save-btn");
  uuidBox.textContent = `${t.common.uuidPrefix}: ${uuid}`;

  function setStatus(message, state = "") {
    setStatusMessage(statusEl, message, state);
  }

  const limitedGroups = ["tally_q20", "tally_q22", "tally_q25", "tally_q27", "tally_q29"];

  function collectValues() {
    const data = new FormData(form);
    const values = {};
    const files = {};

    for (const [key, rawValue] of data.entries()) {
      if (rawValue instanceof File) {
        if (!rawValue.name) {
          continue;
        }
        const meta = { name: rawValue.name, size: rawValue.size, type: rawValue.type || "" };
        files[key] = meta;
        values[key] = meta.name;
        continue;
      }

      const value = String(rawValue || "").trim();
      if (!value) {
        continue;
      }

      if (values[key]) {
        if (Array.isArray(values[key])) {
          values[key].push(value);
        } else {
          values[key] = [values[key], value];
        }
      } else {
        values[key] = value;
      }
    }

    return { values, files };
  }

  form.addEventListener("change", () => toggleConditionBlocks(form));
  form.addEventListener("input", () => toggleConditionBlocks(form));
  form.addEventListener("change", (event) => {
    clearFieldErrorState(event.target);
  });
  form.addEventListener("input", (event) => {
    clearFieldErrorState(event.target);
  });
  toggleConditionBlocks(form);
  enforceCheckboxLimit(form, limitedGroups, 4, setStatus, content.errors.maxFour);

  form.addEventListener("change", (event) => {
    toggleConditionBlocks(form);
    enforceCheckboxLimit(form, limitedGroups, 4, setStatus, content.errors.maxFour, event.target);
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (showFirstInvalidControl(form, setStatus, t)) {
      return;
    }

    const hasTargetCountry = candidateTallyMeta.countryRows.some((row) => {
      return Array.from(form.querySelectorAll(`input[name="${row.field}"]`)).some((input) => input.checked);
    });
    if (!hasTargetCountry) {
      setStatus(`${t.common.validation.required} ${content.overviewMatrixTitle}. ${t.common.validation.checkHighlighted}`, "error");
      focusField(form.querySelector(`input[name="${candidateTallyMeta.countryRows[0].field}"]`));
      return;
    }
    if (!validateVisibleCheckboxGroup(form, "tally_q02", content.mobilityTypeTitle, setStatus, t, 1, 2)) {
      return;
    }
    if (!validateVisibleCheckboxGroup(form, "tally_q19", content.questions.q19, setStatus, t, 1, 5)) {
      return;
    }
    if (
      (form.querySelector('input[name="tally_q06"]:checked') || {}).value === "J’ai des contraintes ou préférences horaires" &&
      !candidateTallyMeta.scheduleRows.every((row) => validateVisibleCheckboxGroup(form, row.field, `${content.questions.q07} - ${row.label}`, setStatus, t))
    ) {
      return;
    }
    for (const row of candidateTallyMeta.documentsRows) {
      if (!validateVisibleCheckboxGroup(form, row.field, `${content.questions.q10} - ${row.label}`, setStatus, t, 1, 1)) {
        return;
      }
    }
    for (const row of candidateTallyMeta.languageRows) {
      if (!validateVisibleCheckboxGroup(form, row.field, `${content.questions.q18} - ${row.label}`, setStatus, t, 1, 1)) {
        return;
      }
    }
    const sectorGroupValidations = [
      ["tally_q20", content.sectorTitles.vente],
      ["tally_q22", content.sectorTitles.nettoyage],
      ["tally_q25", content.sectorTitles.hotel],
      ["tally_q27", content.sectorTitles.agri],
      ["tally_q29", content.sectorTitles.polyvalent],
    ];
    for (const [name, label] of sectorGroupValidations) {
      if (!validateVisibleCheckboxGroup(form, name, label, setStatus, t, 1, 4)) {
        return;
      }
    }

    const { values, files } = collectValues();
    const activeRankingIndexes = candidateTallyMeta.rankingOptions
      .map((_, index) => index)
      .filter((index) => {
        const control = form.querySelector(`select[name="rank__tally_q17__${index}"]`);
        return control && !control.disabled;
      });

    let rankingSummary = [];
    if (activeRankingIndexes.length) {
      const rankSelections = activeRankingIndexes.map((index) => ({
        option: candidateTallyMeta.rankingOptions[index],
        rank: Number(values[`rank__tally_q17__${index}`] || 0)
      }));
      const seenRanks = rankSelections.map((item) => item.rank).filter(Boolean);
      const uniqueRanks = new Set(seenRanks);
      if (seenRanks.length !== activeRankingIndexes.length || uniqueRanks.size !== seenRanks.length) {
        setStatus(`${content.rankingError} ${t.common.validation.checkHighlighted}`, "error");
        const firstRankingField = form.querySelector(`select[name="rank__tally_q17__${activeRankingIndexes[0]}"]`);
        focusField(firstRankingField);
        return;
      }

      rankingSummary = rankSelections
        .sort((a, b) => a.rank - b.rank)
        .map((item) => `${item.rank}. ${item.option}`);
    }

    const normalized = {};
    Object.entries(values).forEach(([key, value]) => {
      if (key.startsWith("rank__")) {
        return;
      }
      if (Array.isArray(value)) {
        normalized[key] = value;
      } else {
        normalized[key] = value;
      }
    });

    normalized.tally_q17 = rankingSummary.join(" > ");
    normalized.tally_q36 = files["file__tally_q36"] ? files["file__tally_q36"].name : "";

    const rawAnswers = humanizeCandidateRawAnswers(normalized, files["file__tally_q36"] || null, rankingSummary);

    const targetCountries = candidateTallyMeta.countryRows
      .filter((row) => Array.isArray(normalized[row.field]) && normalized[row.field].includes("Je veux y travailler"))
      .map((row) => row.label);

    const languageSummary = candidateTallyMeta.languageRows
      .map((row) => `${row.label}: ${Array.isArray(normalized[row.field]) ? normalized[row.field].join(", ") : ""}`)
      .filter((line) => !line.endsWith(": "));

    const skillsSummary = [
      normalized.tally_q20 || [],
      normalized.tally_q22 || [],
      normalized.tally_q25 || [],
      normalized.tally_q27 || [],
      normalized.tally_q29 || []
    ].flat();

    const fields = {
      uuid,
      id_tally: uuid,
      tally_form_id: candidateTallyMeta.formId,
      tally_respondent_id: uuid,
      tally_submitted_at: new Date().toISOString(),
      tally_raw_json: JSON.stringify(rawAnswers),
      nom: `${normalized.tally_q31 || ""} ${normalized.tally_q32 || ""}`.trim(),
      email: normalized.tally_q33 || "",
      pays: targetCountries.join(" | "),
      metier: Array.isArray(normalized.tally_q19) ? normalized.tally_q19.join(" | ") : (normalized.tally_q19 || ""),
      competences: skillsSummary.join(" | "),
      langues: languageSummary.join(" | "),
      mobilite: Array.isArray(normalized.tally_q02) ? normalized.tally_q02.join(" | ") : (normalized.tally_q02 || ""),
      disponibilite: [normalized.tally_q09 || "", ...(Array.isArray(normalized.tally_q08) ? normalized.tally_q08 : [])].filter(Boolean).join(" | "),
      form_version: "2026-06-tally-candidate-v1",
      source_page: "candidate-questionnaire",
      ui_language: lang,
      flow_role: "candidate",
      ...Object.fromEntries(
        Object.entries(normalized).map(([key, value]) => [
          key.replace(/^raw_/, ""),
          Array.isArray(value) ? value.join(" | ") : value
        ])
      )
    };
    if (inviteToken) {
      fields.invite_token = inviteToken;
    }

    saveBtn.disabled = true;
    setStatus(t.common.saving);

    try {
      const response = await fetch(`/api/forms/${FORM_ID}/record`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: JSON.stringify({ fields })
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(payload.error || `${t.common.saveErrorPrefix} (${response.status})`);
      }
      setStatus(t.common.saved, "success");
    } catch (error) {
      const message = error && error.message ? error.message : t.common.saveErrorPrefix;
      setStatus(`${t.common.saveErrorPrefix}: ${message}`, "error");
    } finally {
      saveBtn.disabled = false;
    }
  });
}

function questionnaireTemplate(page, lang, t, data) {
  const isCandidate = page === "candidate-questionnaire";
  return `
    ${nav(page, lang, t)}
    <main id="main-content" class="questionnaire-shell" tabindex="-1">
      <div class="shell questionnaire-grid">
        <section class="questionnaire-card">
          <div class="questionnaire-hero">
            <div class="eyebrow">${data.eyebrow}</div>
            <h1>${data.title}</h1>
            <p class="lede">${data.lede}</p>
          </div>
          <p class="mini-note">${t.common.questionnaireNote}</p>

          <form class="questionnaire-form" id="questionnaire-form" data-role="${isCandidate ? "candidate" : "employer"}" novalidate>
            ${isCandidate ? `
              <section class="form-section">
                <h3>${data.sections.mobility}</h3>
                <div class="form-grid">
                  <label class="field">
                    <span>${data.fields.residenceCountry}</span>
                    <input type="text" name="candidate_residence_country" required>
                  </label>
                  <label class="field">
                    <span>${data.fields.mobilityType}</span>
                    <select name="candidate_mobility_type" required>
                      <option value=""></option>
                      ${data.options.mobilityType.map((option) => `<option value="${option}">${option}</option>`).join("")}
                    </select>
                  </label>
                </div>
                <fieldset class="fieldset">
                  <legend>${data.fields.targetCountries}</legend>
                  ${choicePills("candidate_target_countries", data.options.targetCountries)}
                </fieldset>
                <label class="field">
                  <span>${data.fields.availability}</span>
                  <select name="candidate_availability" required>
                    <option value=""></option>
                    ${data.options.availability.map((option) => `<option value="${option}">${option}</option>`).join("")}
                  </select>
                </label>
              </section>

              <section class="form-section">
                <h3>${data.sections.profile}</h3>
                <fieldset class="fieldset">
                  <legend>${data.fields.sectors}</legend>
                  ${choicePills("candidate_sectors", data.options.sectors)}
                </fieldset>
                <div class="form-grid">
                  <label class="field">
                    <span>${data.fields.experienceLevel}</span>
                    <select name="candidate_experience_level" required>
                      <option value=""></option>
                      ${data.options.experienceLevel.map((option) => `<option value="${option}">${option}</option>`).join("")}
                    </select>
                  </label>
                  <fieldset class="fieldset">
                    <legend>${data.fields.languages}</legend>
                    ${choicePills("candidate_languages", data.options.languages)}
                  </fieldset>
                </div>
              </section>

              <section class="form-section">
                <h3>${data.sections.contact}</h3>
                <div class="form-grid">
                  <label class="field">
                    <span>${data.fields.fullName}</span>
                    <input type="text" name="candidate_full_name" autocomplete="name" required>
                  </label>
                  <label class="field">
                    <span>${data.fields.email}</span>
                    <input type="email" name="email" autocomplete="email" inputmode="email" required>
                  </label>
                  <label class="field">
                    <span>${data.fields.phone}</span>
                    <input type="tel" name="candidate_phone" autocomplete="tel" inputmode="tel" required>
                  </label>
                  <label class="field">
                    <span>${data.fields.city}</span>
                    <input type="text" name="candidate_city" autocomplete="address-level2" required>
                  </label>
                </div>
                <label class="field">
                  <span>${data.fields.notes}</span>
                  <textarea name="candidate_notes"></textarea>
                </label>
              </section>
            ` : `
              <section class="form-section">
                <h3>${data.sections.need}</h3>
                <div class="form-grid">
                  <label class="field">
                    <span>${data.fields.companyName}</span>
                    <input type="text" name="employer_company_name" autocomplete="organization" required>
                  </label>
                  <label class="field">
                    <span>${data.fields.workLocation}</span>
                    <input type="text" name="employer_work_location" required>
                  </label>
                  <label class="field">
                    <span>${data.fields.sector}</span>
                    <select name="employer_sector" required>
                      <option value=""></option>
                      ${data.options.sector.map((option) => `<option value="${option}">${option}</option>`).join("")}
                    </select>
                  </label>
                  <label class="field">
                    <span>${data.fields.recruitCount}</span>
                    <select name="employer_recruit_count" required>
                      <option value=""></option>
                      ${data.options.recruitCount.map((option) => `<option value="${option}">${option}</option>`).join("")}
                    </select>
                  </label>
                </div>
                <label class="field">
                  <span>${data.fields.startDate}</span>
                  <input type="text" name="employer_start_date" required>
                </label>
              </section>

              <section class="form-section">
                <h3>${data.sections.conditions}</h3>
                <fieldset class="fieldset">
                  <legend>${data.fields.languagesRequired}</legend>
                  ${choicePills("employer_languages_required", data.options.languagesRequired)}
                </fieldset>
                <div class="form-grid">
                  <label class="field">
                    <span>${data.fields.contractDuration}</span>
                    <select name="employer_contract_duration" required>
                      <option value=""></option>
                      ${data.options.contractDuration.map((option) => `<option value="${option}">${option}</option>`).join("")}
                    </select>
                  </label>
                  <label class="field">
                    <span>${data.fields.weeklyHours}</span>
                    <select name="employer_weekly_hours" required>
                      <option value=""></option>
                      ${data.options.weeklyHours.map((option) => `<option value="${option}">${option}</option>`).join("")}
                    </select>
                  </label>
                </div>
                <fieldset class="fieldset">
                  <legend>${data.fields.installationSupport}</legend>
                  ${choicePills("employer_installation_support", data.options.installationSupport)}
                </fieldset>
                <fieldset class="fieldset">
                  <legend>${data.fields.criticalCriteria}</legend>
                  ${choicePills("employer_critical_criteria", data.options.criticalCriteria)}
                </fieldset>
              </section>

              <section class="form-section">
                <h3>${data.sections.contact}</h3>
                <div class="form-grid">
                  <label class="field">
                    <span>${data.fields.contactName}</span>
                    <input type="text" name="employer_contact_name" autocomplete="name" required>
                  </label>
                  <label class="field">
                    <span>${data.fields.email}</span>
                    <input type="email" name="email" autocomplete="email" inputmode="email" required>
                  </label>
                  <label class="field">
                    <span>${data.fields.phone}</span>
                    <input type="tel" name="employer_phone" autocomplete="tel" inputmode="tel" required>
                  </label>
                </div>
                <label class="field">
                  <span>${data.fields.notes}</span>
                  <textarea name="employer_notes"></textarea>
                </label>
              </section>
            `}

            <section class="form-section">
              <label class="checkbox-pill consent-pill">
                <input type="checkbox" name="consent_rgpd" value="yes" required>
                <span>${t.common.consent}</span>
              </label>
            </section>

            <div class="questionnaire-actions">
              <button class="primary-action" type="submit" id="save-btn">${t.common.submit}</button>
              <a class="ghost-action" href="${pageUrl(isCandidate ? "candidate-landing" : "employer-landing", lang)}">${t.common.ctaBackHome}</a>
            </div>
            <div class="status" id="status" role="status" aria-live="polite"></div>
          </form>
        </section>

        <aside class="questionnaire-card">
          <h2>${t.common.matchingTitle}</h2>
          ${list(t.common.matchingBullets)}
          <div class="uuid-box" id="uuid-box"></div>
          <div style="height: 1rem;"></div>
          <h2>${t.common.futureTitle}</h2>
          ${list(t.common.futureBullets)}
          <div style="height: 1rem;"></div>
          <p class="mini-note">${data.helper}</p>
        </aside>
      </div>
    </main>
    ${footer(t)}
  `;
}

function createUuid() {
  if (window.crypto && typeof window.crypto.randomUUID === "function") {
    return window.crypto.randomUUID();
  }
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (char) => {
    const random = Math.random() * 16 | 0;
    const value = char === "x" ? random : (random & 0x3 | 0x8);
    return value.toString(16);
  });
}

function storageKey(role) {
  return `grist-custom-forms:${FORM_ID}:${role}:uuid`;
}

function getUuid(role) {
  let uuid = localStorage.getItem(storageKey(role));
  if (!uuid) {
    uuid = createUuid();
    localStorage.setItem(storageKey(role), uuid);
  }
  return uuid;
}

function aggregateFormData(form) {
  const data = new FormData(form);
  const result = {};
  for (const [key, value] of data.entries()) {
    const clean = typeof value === "string" ? value.trim() : value;
    if (result[key]) {
      if (Array.isArray(result[key])) {
        result[key].push(clean);
      } else {
        result[key] = [result[key], clean];
      }
    } else {
      result[key] = clean;
    }
  }

  Object.keys(result).forEach((key) => {
    if (Array.isArray(result[key])) {
      result[key] = JSON.stringify(result[key]);
    }
  });

  return result;
}

function attachQuestionnaireBehavior(page, lang, t) {
  const form = document.getElementById("questionnaire-form");
  if (!form) {
    return;
  }

  const role = form.dataset.role;
  const uuid = getUuid(role);
  const statusEl = document.getElementById("status");
  const uuidBox = document.getElementById("uuid-box");
  const saveBtn = document.getElementById("save-btn");
  uuidBox.textContent = `${t.common.uuidPrefix}: ${uuid}`;

  function setStatus(message, state = "") {
    setStatusMessage(statusEl, message, state);
  }

  form.addEventListener("change", (event) => {
    clearFieldErrorState(event.target);
  });
  form.addEventListener("input", (event) => {
    clearFieldErrorState(event.target);
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (showFirstInvalidControl(form, setStatus, t)) {
      return;
    }

    if (role === "candidate") {
      if (!validateVisibleCheckboxGroup(form, "candidate_target_countries", data.fields.targetCountries, setStatus, t)) {
        return;
      }
      if (!validateVisibleCheckboxGroup(form, "candidate_sectors", data.fields.sectors, setStatus, t)) {
        return;
      }
      if (!validateVisibleCheckboxGroup(form, "candidate_languages", data.fields.languages, setStatus, t)) {
        return;
      }
    } else {
      if (!validateVisibleCheckboxGroup(form, "employer_languages_required", data.fields.languagesRequired, setStatus, t)) {
        return;
      }
      if (!validateVisibleCheckboxGroup(form, "employer_installation_support", data.fields.installationSupport, setStatus, t)) {
        return;
      }
      if (!validateVisibleCheckboxGroup(form, "employer_critical_criteria", data.fields.criticalCriteria, setStatus, t)) {
        return;
      }
    }

    const fields = aggregateFormData(form);
    fields.uuid = uuid;
    fields.flow_role = role;
    fields.ui_language = lang;
    fields.source_page = page;
    fields.submitted_at = new Date().toISOString();
    fields.form_version = "2026-06-home-landing-v1";

    saveBtn.disabled = true;
    setStatus(t.common.saving);

    try {
      const response = await fetch(`/api/forms/${FORM_ID}/record`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: JSON.stringify({ fields })
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(payload.error || `${t.common.saveErrorPrefix} (${response.status})`);
      }
      setStatus(t.common.saved, "success");
    } catch (error) {
      const message = error && error.message ? error.message : t.common.saveErrorPrefix;
      setStatus(`${t.common.saveErrorPrefix}: ${message}`, "error");
    } finally {
      saveBtn.disabled = false;
    }
  });
}

function render() {
  const root = document.getElementById("app");
  const page = document.body.dataset.page;
  const lang = currentLang();
  const t = copy[lang];
  setDocumentLang(lang);

  if (page === "home") {
    root.innerHTML = homeTemplate(lang, t);
    return;
  }

  if (page === "stat") {
    root.innerHTML = `
      ${nav("stat", lang, t)}
      <main id="main-content" class="section" tabindex="-1">
        <div class="shell">
          <div class="panel">
            <h1>${t.statPage.title}</h1>
            <p>${t.statPage.loading}</p>
          </div>
        </div>
      </main>
      ${footer(t)}
    `;
    loadPublicStats()
      .then((data) => {
        root.innerHTML = statTemplate(lang, t, data);
      })
      .catch(() => {
        root.innerHTML = `
          ${nav("stat", lang, t)}
          <main id="main-content" class="section" tabindex="-1">
            <div class="shell">
              <div class="panel">
                <h1>${t.statPage.title}</h1>
                <p>${t.statPage.error}</p>
              </div>
            </div>
          </main>
          ${footer(t)}
        `;
      });
    return;
  }

  if (page === "candidate-landing") {
    root.innerHTML = landingTemplate(page, lang, t, t.candidateLanding);
    return;
  }

  if (page === "employer-landing") {
    root.innerHTML = employerLandingTemplate(lang, t);
    return;
  }

  if (page === "candidate-questionnaire") {
    root.innerHTML = candidateTallyQuestionnaireTemplate(lang, t);
    attachCandidateTallyBehavior(lang, t);
    return;
  }

  if (page === "employer-questionnaire") {
    root.innerHTML = employerTallyQuestionnaireTemplate(lang, t);
    attachEmployerTallyBehavior(lang, t);
  }
}

render();
