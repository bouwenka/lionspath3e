(function () {
  'use strict';

  const BLS_SOURCE_URL = 'https://www.bls.gov/emp/tables/occupational-projections-and-characteristics.htm';
  const COUNSELING_URL = 'https://sites.google.com/lcps.k12.va.us/lchscounseling/home';

  // U.S. Bureau of Labor Statistics, 2024 median pay and 2024-2034 projections.
  // Values are national estimates and are conversation starters, not local wage promises.
  const CAREERS = {
    veterinarian: ['Veterinarian', '$125,510', 'Doctoral or professional degree', '+9.6%', '3,000', '29-1131'],
    vetTech: ['Veterinary technologist or technician', '$45,980', "Associate's degree", '+9.1%', '14,300', '29-2056'],
    animalTrainer: ['Animal trainer', '$38,750', 'High school diploma plus on-the-job training', '+5.1%', '7,100', '39-2011'],
    animalCaretaker: ['Animal caretaker', '$33,470', 'High school diploma plus on-the-job training', '+12.1%', '74,600', '39-2021'],
    animalBreeder: ['Animal breeder', '$52,000', 'High school diploma', '+2.4%', '1,200', '45-2021'],
    animalScientist: ['Animal scientist', '$79,120', "Bachelor's degree", '+5.8%', '200', '19-1011'],
    foodScientist: ['Food scientist or technologist', '$85,310', "Bachelor's degree", '+6.5%', '1,200', '19-1012'],
    plantScientist: ['Soil and plant scientist', '$71,410', "Bachelor's degree", '+5.4%', '1,700', '19-1013'],
    agTechnician: ['Agricultural technician', '$46,790', "Associate's degree", '+4.3%', '2,900', '19-4012'],
    landscapeArchitect: ['Landscape architect', '$79,660', "Bachelor's degree", '+3.5%', '1,700', '17-1012'],
    conservationScientist: ['Conservation scientist', '$67,950', "Bachelor's degree", '+3.4%', '2,500', '19-1031'],
    groundskeeper: ['Landscaping or groundskeeping worker', '$38,090', 'No formal credential; on-the-job training', '+3.6%', '158,200', '37-3011'],
    pesticideApplicator: ['Pesticide handler or applicator', '$45,200', 'High school diploma plus on-the-job training', '+3.8%', '4,100', '37-3012'],
    treeTrimmer: ['Tree trimmer or pruner', '$50,430', 'High school diploma plus on-the-job training', '+3.3%', '7,400', '37-3013'],
    landscapeSupervisor: ['Landscaping and groundskeeping supervisor', '$56,170', 'High school diploma plus related experience', '+2.3%', '23,200', '37-1012'],

    managementAnalyst: ['Management analyst', '$101,190', "Bachelor's degree", '+8.8%', '98,100', '13-1111'],
    eventPlanner: ['Meeting, convention, or event planner', '$59,440', "Bachelor's degree", '+4.8%', '15,500', '13-1121'],
    trainingSpecialist: ['Training and development specialist', '$65,850', "Bachelor's degree", '+10.8%', '43,900', '13-1151'],
    marketResearch: ['Market research analyst or marketing specialist', '$76,950', "Bachelor's degree", '+6.7%', '87,200', '13-1161'],
    accountant: ['Accountant or auditor', '$81,680', "Bachelor's degree", '+4.6%', '124,200', '13-2011'],
    financialAnalyst: ['Financial and investment analyst', '$101,350', "Bachelor's degree", '+5.7%', '25,100', '13-2051'],
    financialAdvisor: ['Personal financial advisor', '$102,140', "Bachelor's degree", '+9.6%', '24,100', '13-2052'],
    publicRelations: ['Public relations specialist', '$69,780', "Bachelor's degree", '+4.8%', '27,600', '27-3031'],
    hrSpecialist: ['Human resources specialist', '$72,910', "Bachelor's degree", '+6.2%', '81,800', '13-1071'],
    logistician: ['Logistician', '$80,880', "Bachelor's degree", '+16.7%', '26,400', '13-1081'],
    projectManager: ['Project management specialist', '$100,750', "Bachelor's degree", '+5.6%', '78,200', '13-1082'],
    marketingManager: ['Marketing manager', '$161,030', "Bachelor's degree plus related experience", '+6.6%', '34,300', '11-2021'],

    systemsAnalyst: ['Computer systems analyst', '$103,790', "Bachelor's degree", '+8.7%', '34,200', '15-1211'],
    infoSecurity: ['Information security analyst', '$124,910', "Bachelor's degree plus related experience", '+28.5%', '16,000', '15-1212'],
    networkSupport: ['Computer network support specialist', '$73,340', "Associate's degree", '+1.8%', '9,600', '15-1231'],
    networkArchitect: ['Computer network architect', '$130,390', "Bachelor's degree plus related experience", '+11.9%', '11,200', '15-1241'],
    databaseArchitect: ['Database architect', '$135,980', "Bachelor's degree plus related experience", '+8.7%', '4,000', '15-1243'],
    softwareDeveloper: ['Software developer', '$133,080', "Bachelor's degree", '+15.8%', '115,200', '15-1252'],
    qaTester: ['Software quality assurance analyst or tester', '$102,610', "Bachelor's degree", '+10.0%', '14,000', '15-1253'],
    webDeveloper: ['Web developer', '$90,930', "Bachelor's degree", '+7.5%', '5,400', '15-1254'],
    digitalDesigner: ['Web and digital interface designer', '$98,090', "Bachelor's degree", '+7.0%', '9,100', '15-1255'],
    dataScientist: ['Data scientist', '$112,590', "Bachelor's degree", '+33.5%', '23,400', '15-2051'],
    operationsAnalyst: ['Operations research analyst', '$91,290', "Bachelor's degree", '+21.5%', '9,600', '15-2031'],
    statistician: ['Statistician', '$103,300', "Master's degree", '+8.5%', '2,000', '15-2041'],
    actuary: ['Actuary', '$125,770', "Bachelor's degree", '+21.8%', '2,400', '15-2011'],

    constructionManager: ['Construction manager', '$106,980', "Bachelor's degree plus on-the-job training", '+8.7%', '46,800', '11-9021'],
    civilEngineer: ['Civil engineer', '$99,590', "Bachelor's degree", '+5.0%', '23,600', '17-2051'],
    electricalEngineer: ['Electrical engineer', '$111,910', "Bachelor's degree", '+7.2%', '11,700', '17-2071'],
    industrialEngineer: ['Industrial engineer', '$101,140', "Bachelor's degree", '+11.0%', '25,200', '17-2112'],
    mechanicalEngineer: ['Mechanical engineer', '$102,320', "Bachelor's degree", '+9.1%', '18,100', '17-2141'],
    computerHardwareEngineer: ['Computer hardware engineer', '$155,020', "Bachelor's degree", '+7.3%', '4,700', '17-2061'],
    engineeringTechnician: ['Electrical or electronic engineering technician', '$77,180', "Associate's degree", '+0.6%', '8,400', '17-3023'],
    mechatronicsTechnician: ['Electro-mechanical or mechatronics technician', '$70,760', "Associate's degree", '+1.1%', '1,300', '17-3024'],
    surveyingTechnician: ['Surveying or mapping technician', '$51,940', 'High school diploma plus on-the-job training', '+4.5%', '7,600', '17-3031'],
    carpenter: ['Carpenter', '$59,310', 'High school diploma plus apprenticeship', '+4.5%', '74,100', '47-2031'],
    constructionLaborer: ['Construction laborer', '$46,730', 'No formal credential; on-the-job training', '+7.3%', '129,400', '47-2061'],
    electrician: ['Electrician', '$62,350', 'High school diploma plus apprenticeship', '+9.5%', '81,000', '47-2111'],
    plumber: ['Plumber, pipefitter, or steamfitter', '$62,970', 'High school diploma plus apprenticeship', '+4.5%', '44,000', '47-2152'],
    hvac: ['HVAC mechanic or installer', '$59,810', 'Postsecondary certificate plus on-the-job training', '+8.1%', '40,100', '49-9021'],
    welder: ['Welder, cutter, solderer, or brazer', '$51,000', 'High school diploma plus technical/on-the-job training', '+2.2%', '45,600', '51-4121'],
    ironWorker: ['Structural iron or steel worker', '$62,700', 'High school diploma plus apprenticeship', '+4.4%', '5,500', '47-2221'],
    cncProgrammer: ['Computer numerically controlled tool programmer', '$65,670', 'Postsecondary certificate plus on-the-job training', '+12.8%', '3,100', '51-9162'],
    industrialMechanic: ['Industrial machinery mechanic', '$63,760', 'High school diploma plus on-the-job training', '+16.1%', '45,700', '49-9041'],
    maintenanceTechnician: ['General maintenance and repair worker', '$48,620', 'High school diploma plus on-the-job training', '+3.8%', '159,800', '49-9071'],
    solarInstaller: ['Solar photovoltaic installer', '$51,860', 'High school diploma plus on-the-job training', '+42.1%', '4,100', '47-2231'],
    windTechnician: ['Wind turbine service technician', '$62,580', 'Postsecondary certificate plus on-the-job training', '+49.9%', '2,300', '49-9081'],
    lineInstaller: ['Electrical power-line installer or repairer', '$92,560', 'High school diploma plus on-the-job training', '+6.6%', '10,700', '49-9051'],
    boilerOperator: ['Stationary engineer or boiler operator', '$75,190', 'High school diploma plus on-the-job training', '+2.2%', '3,800', '51-8021'],
    autoTechnician: ['Automotive service technician or mechanic', '$49,670', 'Postsecondary certificate plus on-the-job training', '+4.2%', '70,000', '49-3023'],
    autoBody: ['Automotive body repairer', '$51,680', 'High school diploma plus on-the-job training', '+1.6%', '14,600', '49-3021'],
    dieselMechanic: ['Diesel service technician or mechanic', '$60,640', 'High school diploma plus on-the-job training', '+2.4%', '26,500', '49-3031'],
    heavyEquipmentMechanic: ['Mobile heavy equipment mechanic', '$63,980', 'High school diploma plus on-the-job training', '+5.8%', '16,500', '49-3042'],
    farmEquipmentMechanic: ['Farm equipment mechanic', '$52,080', 'High school diploma plus on-the-job training', '+11.0%', '3,700', '49-3041'],
    rvTechnician: ['Recreational vehicle service technician', '$50,540', 'High school diploma plus on-the-job training', '+11.5%', '2,800', '49-3092'],
    avionicsTechnician: ['Avionics technician', '$81,390', 'Postsecondary certificate', '+8.2%', '1,800', '49-2091'],
    securityInstaller: ['Security or fire alarm systems installer', '$59,300', 'High school diploma plus on-the-job training', '+10.4%', '9,400', '49-2098'],
    medicalEquipmentRepairer: ['Medical equipment repairer', '$62,630', "Associate's degree plus on-the-job training", '+12.9%', '7,300', '49-9062'],

    registeredNurse: ['Registered nurse', '$93,600', "Bachelor's degree", '+4.9%', '189,100', '29-1141'],
    licensedPracticalNurse: ['Licensed practical or vocational nurse', '$62,340', 'Postsecondary certificate', '+2.6%', '54,400', '29-2061'],
    nursingAssistant: ['Nursing assistant', '$39,530', 'Postsecondary certificate', '+2.3%', '204,100', '31-1131'],
    homeHealthAide: ['Home health or personal care aide', '$34,900', 'High school diploma', '+17.0%', '765,800', '31-1120'],
    medicalAssistant: ['Medical assistant', '$44,200', 'Postsecondary certificate', '+12.5%', '112,300', '31-9092'],
    healthInformation: ['Health information technologist or medical registrar', '$67,310', "Associate's degree", '+14.7%', '3,200', '29-9021'],
    respiratoryTherapist: ['Respiratory therapist', '$80,450', "Associate's degree", '+12.1%', '8,800', '29-1126'],
    sonographer: ['Diagnostic medical sonographer', '$89,340', "Associate's degree", '+13.0%', '5,800', '29-2032'],
    radiologicTechnologist: ['Radiologic technologist or technician', '$77,660', "Associate's degree", '+4.3%', '12,900', '29-2034'],
    occupationalTherapist: ['Occupational therapist', '$98,340', "Master's degree", '+13.8%', '10,200', '29-1122'],
    occupationalTherapyAssistant: ['Occupational therapy assistant', '$68,340', "Associate's degree", '+19.2%', '7,200', '31-2011'],
    physicalTherapist: ['Physical therapist', '$101,020', 'Doctoral or professional degree', '+10.9%', '13,200', '29-1123'],
    physicalTherapyAssistant: ['Physical therapist assistant', '$65,510', "Associate's degree", '+22.0%', '19,800', '31-2021'],
    athleticTrainer: ['Athletic trainer', '$60,250', "Master's degree", '+11.1%', '2,400', '29-9091'],
    exercisePhysiologist: ['Exercise physiologist', '$58,160', "Bachelor's degree", '+9.5%', '1,700', '29-1128'],
    fitnessTrainer: ['Exercise trainer or group fitness instructor', '$46,180', 'High school diploma plus certification/on-the-job training', '+11.9%', '74,200', '39-9031'],
    dietitian: ['Dietitian or nutritionist', '$73,850', "Bachelor's degree plus internship", '+5.5%', '6,200', '29-1031'],
    emt: ['Emergency medical technician', '$41,340', 'Postsecondary certificate', '+5.1%', '14,100', '29-2042'],
    paramedic: ['Paramedic', '$58,410', 'Postsecondary certificate', '+5.0%', '4,900', '29-2043'],

    policeOfficer: ['Police or sheriff patrol officer', '$76,290', 'High school diploma plus academy/on-the-job training', '+3.1%', '53,700', '33-3051'],
    firefighter: ['Firefighter', '$59,530', 'Postsecondary certificate plus on-the-job training', '+3.4%', '27,100', '33-2011'],
    fireInspector: ['Fire inspector or investigator', '$78,060', 'Postsecondary education plus related experience', '+3.8%', '1,500', '33-2021'],
    emergencyManager: ['Emergency management director', '$86,130', "Bachelor's degree plus related experience", '+3.0%', '1,000', '11-9161'],
    forensicTechnician: ['Forensic science technician', '$67,440', "Bachelor's degree", '+12.8%', '2,900', '19-4092'],
    safetySpecialist: ['Occupational health and safety specialist', '$83,910', "Bachelor's degree", '+12.5%', '14,900', '19-5011'],
    communityHealthWorker: ['Community health worker', '$51,030', 'High school diploma plus on-the-job training', '+11.3%', '7,800', '21-1094'],
    socialServiceAssistant: ['Social and human service assistant', '$45,120', 'High school diploma plus on-the-job training', '+6.4%', '50,600', '21-1093'],

    preschoolTeacher: ['Preschool teacher', '$37,120', "Associate's degree", '+4.1%', '65,500', '25-2011'],
    secondaryTeacher: ['Secondary school teacher', '$64,580', "Bachelor's degree", '-1.6%', '66,200', '25-2031'],
    cteTeacher: ['Career and technical education teacher', '$63,910', "Bachelor's degree plus occupational experience", '-1.8%', '6,200', '25-2032'],
    teachingAssistant: ['Teaching assistant', '$35,240', 'Some college, no degree', '-1.5%', '170,400', '25-9045'],
    instructionalCoordinator: ['Instructional coordinator', '$74,720', "Master's degree plus related experience", '+1.3%', '21,900', '25-9031'],
    schoolCounselor: ['School or career counselor', '$65,140', "Master's degree", '+3.5%', '31,000', '21-1012'],

    chef: ['Chef or head cook', '$60,990', 'High school diploma plus related experience', '+7.1%', '24,400', '35-1011'],
    restaurantCook: ['Restaurant cook', '$36,830', 'No formal credential; on-the-job training', '+14.9%', '250,700', '35-2014'],
    foodServiceManager: ['Food service manager', '$65,310', 'High school diploma plus related experience', '+6.4%', '42,000', '11-9051'],
    baker: ['Baker', '$36,650', 'No formal credential; on-the-job training', '+5.6%', '39,900', '51-3011'],
    foodSupervisor: ['Food preparation and serving supervisor', '$42,010', 'High school diploma plus related experience', '+6.0%', '183,900', '35-1012'],

    barber: ['Barber', '$38,960', 'Postsecondary certificate and state license', '+4.1%', '8,400', '39-5011'],
    cosmetologist: ['Hairdresser, hairstylist, or cosmetologist', '$35,250', 'Postsecondary certificate and state license', '+5.6%', '75,800', '39-5012'],
    makeupArtist: ['Theatrical or performance makeup artist', '$50,280', 'Postsecondary certificate', '+8.1%', '1,100', '39-5091'],
    nailTechnician: ['Manicurist or pedicurist', '$34,660', 'Postsecondary certificate and state license', '+7.0%', '24,800', '39-5092'],
    skincareSpecialist: ['Skincare specialist', '$41,560', 'Postsecondary certificate and state license', '+6.7%', '14,500', '39-5094'],
    personalServiceSupervisor: ['Personal service supervisor', '$47,080', 'High school diploma plus related experience', '+6.7%', '16,300', '39-1022'],

    producerDirector: ['Producer or director', '$83,480', "Bachelor's degree plus related experience", '+4.9%', '12,800', '27-2012'],
    videoEditor: ['Film or video editor', '$70,980', "Bachelor's degree", '+4.0%', '3,600', '27-4032'],
    cameraOperator: ['Television, video, or film camera operator', '$68,810', "Bachelor's degree", '+1.2%', '2,900', '27-4031'],
    avTechnician: ['Audio and video technician', '$54,830', 'Postsecondary certificate', '+3.3%', '7,300', '27-4011'],
    photographer: ['Photographer', '$42,520', 'High school diploma plus on-the-job training', '+1.8%', '12,700', '27-4021'],
    editor: ['Editor', '$75,260', "Bachelor's degree plus related experience", '+0.6%', '9,800', '27-3041'],
    technicalWriter: ['Technical writer', '$91,670', "Bachelor's degree plus technical knowledge", '+0.9%', '4,500', '27-3042'],
    writerAuthor: ['Writer or author', '$72,270', "Bachelor's degree", '+3.6%', '13,400', '27-3043'],
    interpreter: ['Interpreter or translator', '$59,440', "Bachelor's degree", '+1.7%', '6,900', '27-3091'],
    artDirector: ['Art director', '$111,040', "Bachelor's degree plus related experience", '+4.2%', '12,300', '27-1011'],
    animator: ['Special effects artist or animator', '$99,800', "Bachelor's degree", '+1.6%', '5,000', '27-1014'],
    graphicDesigner: ['Graphic designer', '$61,300', "Bachelor's degree", '+2.1%', '20,000', '27-1024'],
    interiorDesigner: ['Interior designer', '$63,490', "Bachelor's degree", '+3.2%', '7,800', '27-1025'],
    setDesigner: ['Set or exhibit designer', '$66,280', "Bachelor's degree", '+2.3%', '2,500', '27-1027'],
    choreographer: ['Choreographer', '$55,600', 'High school diploma plus related experience', '+6.1%', '700', '27-2032'],

    environmentalScientist: ['Environmental scientist or specialist', '$80,060', "Bachelor's degree", '+4.4%', '8,500', '19-2041'],
    geoscientist: ['Geoscientist', '$99,240', "Bachelor's degree", '+3.2%', '2,000', '19-2042'],
    chemist: ['Chemist', '$84,150', "Bachelor's degree", '+4.9%', '6,300', '19-2031'],
    materialsScientist: ['Materials scientist', '$104,160', "Bachelor's degree", '+4.9%', '600', '19-2032'],
    microbiologist: ['Microbiologist', '$87,330', "Bachelor's degree", '+4.1%', '1,700', '19-1022'],
    medicalScientist: ['Medical scientist', '$100,590', 'Doctoral or professional degree', '+8.7%', '9,600', '19-1042'],
    biochemist: ['Biochemist or biophysicist', '$103,650', 'Doctoral or professional degree', '+5.8%', '2,900', '19-1021'],
    epidemiologist: ['Epidemiologist', '$83,980', "Master's degree", '+16.2%', '800', '19-1041'],
    biologicalTechnician: ['Biological technician', '$52,000', "Bachelor's degree", '+3.5%', '9,100', '19-4021'],
    chemicalTechnician: ['Chemical technician', '$57,790', "Associate's degree", '+3.7%', '6,700', '19-4031'],
    environmentalTechnician: ['Environmental science and protection technician', '$49,490', "Associate's degree", '+4.0%', '5,600', '19-4042'],
    physicist: ['Physicist', '$166,290', 'Doctoral or professional degree', '+4.0%', '1,700', '19-2012'],
    aerospaceEngineer: ['Aerospace engineer', '$134,830', "Bachelor's degree", '+6.1%', '4,500', '17-2011'],

    urbanPlanner: ['Urban or regional planner', '$83,720', "Master's degree", '+3.4%', '3,400', '19-3051'],
    socialResearchAssistant: ['Social science research assistant', '$58,040', "Bachelor's degree", '+4.4%', '5,200', '19-4061'],
    complianceOfficer: ['Compliance officer', '$78,420', "Bachelor's degree", '+3.0%', '33,300', '13-1041'],
    lawyer: ['Lawyer', '$151,160', 'Doctoral or professional degree', '+4.1%', '31,500', '23-1011'],
    paralegal: ['Paralegal or legal assistant', '$61,010', "Associate's degree", '+0.2%', '39,300', '23-2011'],
    mentalHealthCounselor: ['Mental health or substance-use counselor', '$59,190', "Master's degree plus internship", '+16.8%', '48,300', '21-1018'],
    clinicalPsychologist: ['Clinical or counseling psychologist', '$95,830', 'Doctoral or professional degree', '+11.2%', '4,800', '19-3033'],
    schoolPsychologist: ['School psychologist', '$86,930', "Master's degree plus internship", '+0.7%', '3,800', '19-3034'],
    socialWorker: ['Child, family, or school social worker', '$58,570', "Bachelor's degree", '+3.4%', '35,100', '21-1021'],
    healthcareSocialWorker: ['Healthcare social worker', '$68,090', "Master's degree", '+7.7%', '18,400', '21-1022']
  };

  const GROUPS = {
    animalCare: ['veterinarian', 'vetTech', 'animalTrainer', 'animalCaretaker', 'animalBreeder', 'animalScientist'],
    animalProduction: ['animalScientist', 'agTechnician', 'farmEquipmentMechanic', 'foodScientist', 'conservationScientist', 'animalBreeder'],
    plantScience: ['plantScientist', 'agTechnician', 'foodScientist', 'landscapeArchitect', 'conservationScientist', 'environmentalScientist'],
    turfLandscape: ['groundskeeper', 'landscapeSupervisor', 'landscapeArchitect', 'pesticideApplicator', 'treeTrimmer', 'heavyEquipmentMechanic'],
    marketing: ['marketResearch', 'marketingManager', 'publicRelations', 'eventPlanner', 'managementAnalyst', 'projectManager'],
    businessFinance: ['accountant', 'financialAnalyst', 'financialAdvisor', 'managementAnalyst', 'projectManager', 'hrSpecialist'],
    cyber: ['infoSecurity', 'networkArchitect', 'databaseArchitect', 'softwareDeveloper', 'qaTester', 'systemsAnalyst'],
    software: ['softwareDeveloper', 'webDeveloper', 'qaTester', 'systemsAnalyst', 'dataScientist', 'digitalDesigner'],
    networkIT: ['networkSupport', 'networkArchitect', 'infoSecurity', 'databaseArchitect', 'securityInstaller', 'systemsAnalyst'],
    manufacturing: ['industrialMechanic', 'cncProgrammer', 'welder', 'industrialEngineer', 'maintenanceTechnician', 'mechatronicsTechnician'],
    welding: ['welder', 'ironWorker', 'cncProgrammer', 'industrialMechanic', 'constructionManager', 'safetySpecialist'],
    energy: ['windTechnician', 'solarInstaller', 'lineInstaller', 'electrician', 'boilerOperator', 'electricalEngineer'],
    construction: ['constructionManager', 'carpenter', 'electrician', 'plumber', 'hvac', 'constructionLaborer'],
    automotive: ['autoTechnician', 'dieselMechanic', 'autoBody', 'heavyEquipmentMechanic', 'farmEquipmentMechanic', 'rvTechnician'],
    engineering: ['civilEngineer', 'mechanicalEngineer', 'electricalEngineer', 'industrialEngineer', 'engineeringTechnician', 'mechatronicsTechnician'],
    healthcare: ['registeredNurse', 'medicalAssistant', 'healthInformation', 'respiratoryTherapist', 'sonographer', 'radiologicTechnologist'],
    nursing: ['nursingAssistant', 'licensedPracticalNurse', 'registeredNurse', 'homeHealthAide', 'medicalAssistant', 'healthInformation'],
    sportsMedicine: ['athleticTrainer', 'exercisePhysiologist', 'fitnessTrainer', 'physicalTherapyAssistant', 'physicalTherapist', 'occupationalTherapyAssistant'],
    militaryTransfer: ['logistician', 'infoSecurity', 'emergencyManager', 'avionicsTechnician', 'medicalEquipmentRepairer', 'trainingSpecialist'],
    publicSafety: ['policeOfficer', 'firefighter', 'fireInspector', 'emergencyManager', 'forensicTechnician', 'safetySpecialist'],
    emergencyCare: ['emt', 'paramedic', 'firefighter', 'registeredNurse', 'respiratoryTherapist', 'communityHealthWorker'],
    education: ['preschoolTeacher', 'secondaryTeacher', 'cteTeacher', 'teachingAssistant', 'instructionalCoordinator', 'schoolCounselor'],
    culinary: ['restaurantCook', 'chef', 'foodServiceManager', 'baker', 'foodSupervisor', 'foodScientist'],
    beauty: ['barber', 'cosmetologist', 'makeupArtist', 'nailTechnician', 'skincareSpecialist', 'personalServiceSupervisor'],
    media: ['producerDirector', 'videoEditor', 'cameraOperator', 'avTechnician', 'photographer', 'publicRelations'],
    communications: ['writerAuthor', 'editor', 'technicalWriter', 'publicRelations', 'eventPlanner', 'marketResearch'],
    socialScience: ['urbanPlanner', 'socialResearchAssistant', 'communityHealthWorker', 'complianceOfficer', 'lawyer', 'schoolCounselor'],
    psychology: ['mentalHealthCounselor', 'clinicalPsychologist', 'schoolPsychologist', 'socialWorker', 'communityHealthWorker', 'schoolCounselor'],
    lawPolicy: ['lawyer', 'paralegal', 'complianceOfficer', 'policeOfficer', 'emergencyManager', 'urbanPlanner'],
    dataMath: ['dataScientist', 'operationsAnalyst', 'actuary', 'statistician', 'financialAnalyst', 'systemsAnalyst'],
    environmentalScience: ['environmentalScientist', 'geoscientist', 'conservationScientist', 'environmentalTechnician', 'plantScientist', 'urbanPlanner'],
    lifeScience: ['microbiologist', 'medicalScientist', 'biochemist', 'biologicalTechnician', 'epidemiologist', 'veterinarian'],
    chemistry: ['chemist', 'materialsScientist', 'chemicalTechnician', 'environmentalScientist', 'foodScientist', 'forensicTechnician'],
    physicsEngineering: ['physicist', 'aerospaceEngineer', 'electricalEngineer', 'mechanicalEngineer', 'computerHardwareEngineer', 'avionicsTechnician'],
    healthScience: ['registeredNurse', 'respiratoryTherapist', 'sonographer', 'dietitian', 'healthInformation', 'medicalScientist'],
    forensicScience: ['forensicTechnician', 'policeOfficer', 'fireInspector', 'chemist', 'biologicalTechnician', 'safetySpecialist'],
    languages: ['interpreter', 'publicRelations', 'technicalWriter', 'marketResearch', 'schoolCounselor', 'communityHealthWorker'],
    visualArts: ['graphicDesigner', 'artDirector', 'interiorDesigner', 'digitalDesigner', 'setDesigner', 'photographer'],
    performingArts: ['producerDirector', 'avTechnician', 'cameraOperator', 'videoEditor', 'choreographer', 'eventPlanner'],
    stemResearch: ['dataScientist', 'civilEngineer', 'softwareDeveloper', 'environmentalScientist', 'medicalScientist', 'operationsAnalyst'],
    lifeSkills: ['dietitian', 'communityHealthWorker', 'financialAdvisor', 'socialServiceAssistant', 'healthcareSocialWorker', 'hrSpecialist'],
    educationSupport: ['teachingAssistant', 'schoolCounselor', 'trainingSpecialist', 'projectManager', 'hrSpecialist', 'eventPlanner'],
    fitness: ['athleticTrainer', 'exercisePhysiologist', 'fitnessTrainer', 'physicalTherapyAssistant', 'dietitian', 'communityHealthWorker'],
    transportationSafety: ['autoTechnician', 'safetySpecialist', 'policeOfficer', 'logistician', 'heavyEquipmentMechanic', 'emergencyManager'],
    generalPlanning: ['projectManager', 'managementAnalyst', 'publicRelations', 'hrSpecialist', 'communityHealthWorker', 'trainingSpecialist']
  };

  const PREREQUISITE_OVERRIDES = {
    'Equine Science I': 'Introduction to Animal Systems.',
    'Equine Science, Advanced': 'Equine Science I.',
    'Veterinary Science II': 'Veterinary Science I.',
    'Greenhouse Plant Production Management': 'Horticulture Science.',
    'Turfgrass Management, Advanced': 'Turfgrass Management.',
    'Landscaping II': 'Landscaping I.',
    'Cybersecurity Operations': 'Cybersecurity Fundamentals.',
    'Cybersecurity Operations Advanced': 'Cybersecurity Operations.',
    'Advanced Placement Computer Science': 'Programming or instructor approval.',
    'Computer Networking Software Operations': 'Computer Information Systems.',
    'Computer Networking Software Operations Advanced': 'Computer Networking Software Operations.',
    'Tech Help Desk Intern': 'Computer Information Systems or comparable networking/programming experience; instructor approval may be required.',
    'Welding II': 'Welding I.',
    'Power Generation Design & Function': 'Fundamentals of Power Generation.',
    'Carpentry II': 'Carpentry I.',
    'Carpentry III': 'Carpentry II.',
    'Automotive Technology II': 'Automotive Technology I.',
    'Automotive Technology III': 'Automotive Technology II.',
    'PVCC Mechanical/Electrical Engineering Technology Program': 'Program application/admission and current PVCC placement requirements; confirm eligibility with LCHS Counseling.',
    'Nurse Aide I': 'Introduction to Health & Medical Sciences, application, and program acceptance. Additional health screening and uniform requirements may apply.',
    'Medical Terminology': 'Introduction to Health & Medical Sciences.',
    'Sports Medicine/Athletic Training II Condensed': 'Sports Medicine/Athletic Training I Condensed.',
    'Marine Corps JROTC II': 'Marine Corps JROTC I.',
    'Marine Corps JROTC III': 'Marine Corps JROTC II.',
    'Marine Corps JROTC IV': 'Marine Corps JROTC III.',
    'Fire Fighting I': 'Students must be at least 16 years old, have a current health physical, and complete the required parent orientation.',
    'Emergency Medical Technician I & II': 'Students must meet Virginia Office of EMS age and functional-position requirements. Students generally must be at least 16 on the first day of instruction, or have an approved variance and turn 16 before the course ends.',
    'Teachers for Tomorrow II': 'Teachers for Tomorrow I.',
    'Culinary Arts I': 'Introduction to Culinary Arts.',
    'Culinary Arts II': 'Culinary Arts I.',
    'Cosmetology II': 'Cosmetology I.',
    'Cosmetology III': 'Cosmetology II.',
    'Barbering II': 'Barbering I.',
    'Barbering III': 'Barbering II.',
    'Television & Media Production II': 'Television & Media Production I.',
    'Dual Enrollment English 12 (ENG 111-112)': 'High academic achievement in previous English courses, recommendation, and an overall GPA of 3.0 or higher.',
    'Composition I / English 11 - Yearlong': 'English 9 and English 10. Confirm placement with the English department or school counselor.',
    'English 11 (NCAA)': 'English 9 and English 10.',
    'English 11 Honors (NCAA)': 'High academic achievement in previous English courses, preferably honors, and teacher recommendation.',
    'Leadership': 'Instructor approval.',
    'Newspaper (Weighted)': 'Newspaper I.',
    'Competitive Speech and Debate II': 'Competitive Speech and Debate I or instructor approval.',
    'Competitive Speech and Debate III / IV': 'The previous Competitive Speech and Debate level or instructor approval.',
    'Dual Enrollment Sociology I & II (SOC 200 and SOC 268)': 'Overall GPA of 3.0 or higher and current dual-enrollment eligibility requirements.',
    'Geometry Part II (NCAA)': 'Geometry Part I.',
    'Dual Enrollment Pre-Calculus (MTH 167)': 'Mathematical Analysis and an overall GPA of 3.0 or higher.',
    'Dual Enrollment Statistics (MTH 245)': 'Mathematical Analysis and an overall GPA of 3.2 or higher.',
    'Dual Enrollment Calculus I (MTH 263)': 'Dual Enrollment Pre-Calculus (MTH 167).',
    'Dual Enrollment Calculus II (MTH 264)': 'Dual Enrollment Calculus I (MTH 263).',
    'Biology I Honors (NCAA)': 'An A/B average in Earth Science Honors, or an A average in Earth Science or Environmental Science with teacher recommendation.',
    'Chemistry I (NCAA)': 'Biology and completion of Geometry.',
    'Chemistry I Honors (NCAA)': 'An A/B average in Biology I Honors and completion of Geometry.',
    'AP Chemistry (NCAA)': 'Chemistry and recommendation from the chemistry teacher.',
    'Physics I (NCAA)': 'Completion of Geometry.',
    'AP Physics (NCAA)': 'Mathematical Analysis.',
    'AP French Language & Composition (NCAA)': 'French IV or teacher recommendation.',
    'BRVGS Grade 9 Technology Through the Ages (WH I & WH II)': 'Acceptance through the BRVGS eighth-grade application process.',
    'BRVGS Grade 11 Approved Online Course(s)': 'BRVGS enrollment and approval of the selected online course.',
    'BRVGS Grade 12 Senior Capstone': 'BRVGS enrollment and completion of the required earlier BRVGS sequence.',
    'Blue Ridge Virginia Governor\'s School / Senior Capstone': 'Acceptance through the BRVGS application process and continued good standing in the program.',
    'SOL Academy': 'Placement based on student need and school approval.',
    'CTE Academy': 'School approval and completion of the applicable CTE program requirements.',
    'Adapted Physical Education': 'Placement through the student support/IEP process.',
    'Driver Education Part I - Classroom Phase': 'Students must meet the current age and school eligibility requirements.',
    'ESOL 1': 'Placement is based on WIDA ACCESS for ELLs scores, SOL scores, and teacher input.',
    'ESOL 2': 'Placement is based on current WIDA ACCESS for ELLs or W-APT scores and teacher recommendation.',
    'Advanced Choir': 'Entrance by audition; verify current audition dates and standards with the choral director.',
    'Independent Study': 'Teacher sponsorship, a written study plan, and school approval.',
    'Senior Service': 'Senior status and school approval.',
    'Virtual Virginia Courses': 'School approval and any prerequisite or placement requirement listed for the selected Virtual Virginia course.'
  };

  function cleanText(value) {
    if (typeof value !== 'string') return value;
    return value
      .replace(/([A-Za-z])\uFFFDs\b/g, "$1's")
      .replace(/\uFFFDB\uFFFD/g, '"B"')
      .replace(/\s*\uFFFD\s*/g, ' - ')
      .replace(/\s{2,}/g, ' ')
      .trim();
  }

  function cleanDeep(value) {
    if (Array.isArray(value)) return value.map(cleanDeep);
    if (value && typeof value === 'object') {
      Object.keys(value).forEach(key => { value[key] = cleanDeep(value[key]); });
      return value;
    }
    return cleanText(value);
  }

  function careerRecord(id) {
    const row = CAREERS[id];
    if (!row) return null;
    return {
      job: row[0],
      wage: row[1],
      education: row[2],
      growth: row[3],
      openings: `${row[4]} per year`,
      soc: row[5]
    };
  }

  function careerGroupFor(course) {
    const name = String(course.name || '').toLowerCase();
    const pathway = String(course.pathway || '');

    if (pathway === 'Animal Systems') return /livestock/.test(name) ? 'animalProduction' : 'animalCare';
    if (pathway === 'Plant Systems') return 'plantScience';
    if (pathway === 'Turf & Landscaping') return 'turfLandscape';
    if (pathway === 'Business & Marketing') return 'marketing';
    if (pathway === 'Cybersecurity') return 'cyber';
    if (pathway === 'Information Technology') return /network|help desk/.test(name) ? 'networkIT' : 'software';
    if (pathway === 'Production Systems') {
      if (/weld/.test(name)) return 'welding';
      if (/power|energy/.test(name)) return 'energy';
      return 'manufacturing';
    }
    if (pathway === 'Construction Systems') return 'construction';
    if (pathway === 'Automotive') return 'automotive';
    if (pathway === 'PVCC Engineering Technology') return 'engineering';
    if (pathway === 'Health Science') {
      if (/nurse aide/.test(name)) return 'nursing';
      if (/sports medicine|athletic training/.test(name)) return 'sportsMedicine';
      return 'healthcare';
    }
    if (pathway === 'Military Sciences') return 'militaryTransfer';
    if (pathway === 'Public Safety') return /emergency medical/.test(name) ? 'emergencyCare' : 'publicSafety';
    if (pathway === 'Teacher Training Academy') return 'education';
    if (pathway === 'Culinary Arts') return 'culinary';
    if (pathway === 'Human Services') return 'beauty';
    if (pathway === 'TV Broadcasting') return 'media';
    if (pathway === 'English') return /journalism|newspaper|yearbook/.test(name) ? 'media' : 'communications';
    if (pathway === 'Social Science') {
      if (/psychology|well-being/.test(name)) return 'psychology';
      if (/government|religion|african-american|history of women/.test(name)) return 'lawPolicy';
      return 'socialScience';
    }
    if (pathway === 'Mathematics') return /programming|computer science/.test(name) ? 'software' : 'dataMath';
    if (pathway === 'Science') {
      if (/forensic/.test(name)) return 'forensicScience';
      if (/anatomy/.test(name)) return 'healthScience';
      if (/biology/.test(name)) return 'lifeScience';
      if (/chemistry/.test(name)) return 'chemistry';
      if (/physics/.test(name)) return 'physicsEngineering';
      return 'environmentalScience';
    }
    if (pathway === 'World Languages') return 'languages';
    if (pathway === 'Fine Arts') {
      if (/art|ceramic|drawing/.test(name)) return 'visualArts';
      return 'performingArts';
    }
    if (pathway === 'BRVGS' || /Blue Ridge Virginia Governor/.test(pathway)) return 'stemResearch';
    if (pathway === 'Life Skill Development') return 'lifeSkills';
    if (pathway === 'LCHS Academies & Support') return 'educationSupport';
    if (pathway === 'Health & Physical Education') return /driver/.test(name) ? 'transportationSafety' : 'fitness';
    if (pathway === 'General Electives') return 'generalPlanning';
    return 'generalPlanning';
  }

  function extractPrerequisite(course) {
    if (PREREQUISITE_OVERRIDES[course.name]) return PREREQUISITE_OVERRIDES[course.name];
    const sequence = Array.isArray(course.sequence) ? course.sequence : [];
    const prerequisiteLine = sequence.find(item => /^Prerequisite:/i.test(String(item || '')));
    if (prerequisiteLine) return String(prerequisiteLine).replace(/^Prerequisite:\s*/i, '').trim();
    return 'No prerequisite is listed in the current course guide. Placement, capacity, and scheduling still should be confirmed with LCHS Counseling.';
  }

  function applyCourseEnhancements(courses) {
    if (!Array.isArray(courses)) return;
    courses.forEach(course => {
      cleanDeep(course);
      course.prerequisites = extractPrerequisite(course);
      course.sequence = (course.sequence || []).filter(item => !/^Prerequisite:/i.test(String(item || '')));
      const group = GROUPS[careerGroupFor(course)] || GROUPS.generalPlanning;
      course.careers = group.map(careerRecord).filter(Boolean);
      course.careerSource = BLS_SOURCE_URL;
      course.careerSourceLabel = 'U.S. Bureau of Labor Statistics, 2024-2034 projections';
    });
  }

  window.LIONSPATH_COURSE_ENHANCEMENTS = {
    applyCourseEnhancements,
    blsSource: BLS_SOURCE_URL,
    counselingUrl: COUNSELING_URL
  };
})();
