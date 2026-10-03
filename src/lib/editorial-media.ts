import { z } from 'zod';
import { mediaSchema } from '../types/content';
import data from '../data/editorial-media.json';

export const editorialMedia = z.record(z.string(), mediaSchema).parse(data);
