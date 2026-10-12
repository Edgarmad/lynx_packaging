import type { Language } from '../types/content';

const texts = {
  es: {
    about: 'Nosotros',
    serviceIntro: 'De la idea a la entrega',
    processLabel: 'Explora nuestro proceso',
    supplyIntro: 'Una red de proveedores. Distintas necesidades.',
    supplyLabel: 'Recursos de producción',
    supplierNote: 'Fotografías de Jihong, extraídas de los catálogos del proveedor.',
    projectTitle: 'Hablemos de tu próximo proyecto',
    projectDescription: 'Cuéntanos qué empaque necesitas, desde la primera idea hasta la entrega.',
    contact: 'Contacto',
    viewResources: 'Conoce nuestros recursos de suministro',
    viewService: 'Conoce nuestro servicio integral',
    designCases: 'Casos de diseño',
  },
  en: {
    about: 'About',
    serviceIntro: 'From idea to delivery',
    processLabel: 'Explore our process',
    supplyIntro: 'One supplier network. Different needs.',
    supplyLabel: 'Production resources',
    supplierNote: 'Jihong photographs, extracted from supplier catalogues.',
    projectTitle: 'Let’s talk about your next project',
    projectDescription: 'Tell us about your packaging needs, from the first idea through to delivery.',
    contact: 'Contact',
    viewResources: 'Explore our supply chain resources',
    viewService: 'Explore our one-stop service',
    designCases: 'Design cases',
  },
} satisfies Record<Language, Record<string, string>>;

export function abilityUi(lang: Language) {
  return texts[lang];
}
